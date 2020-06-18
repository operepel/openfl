# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import time
import os
import logging

import numpy as np
import tensorboardX
from threading import Lock

from .. import check_equal, check_not_equal, check_is_in, check_not_in
from ..proto.collaborator_aggregator_interface_pb2 import MessageHeader
from ..proto.collaborator_aggregator_interface_pb2 import Job, JobRequest, JobReply
from ..proto.collaborator_aggregator_interface_pb2 import JOB_DOWNLOAD_MODEL, JOB_QUIT, JOB_TRAIN, JOB_VALIDATE, JOB_YIELD
from ..proto.collaborator_aggregator_interface_pb2 import ModelProto, ModelHeader, TensorProto
from ..proto.collaborator_aggregator_interface_pb2 import ModelDownloadRequest, GlobalModelUpdate
from ..proto.collaborator_aggregator_interface_pb2 import LocalModelUpdate, LocalValidationResults, LocalModelUpdateAck, LocalValidationResultsAck


from tfedlrn.proto.protoutils import dump_proto, load_proto, construct_proto, deconstruct_proto
from tfedlrn.tensor_transformation_pipelines import NoCompressionPipeline

# FIXME: simpler "stats" collection/handling
# FIXME: remove the round tracking/job-result tracking stuff from this?
# Feels like it conflates model aggregation with round management
# FIXME: persistence of the trained weights.
class Aggregator(object):
    """An Aggregator is the central node in federated learning.
    
    Parameters
    ----------
    id : str
        Aggregation ID.
    fed_id : str
        Federation ID.
    col_ids : list of str
        The list of IDs of enrolled collaborators.
    connection : ?
        Used to be ZMQ connection, but deprecated in gRPC.
    init_model_fpath : str
        The location of the initial weight file.
    latest_model_fpath : str
        The file location to store the latest weight.
    best_model_fpath : str
        The file location to store the weight of the best model.
    """
    # FIXME: no selector logic is in place
    def __init__(self,
                 agg_id,
                 fed_id,
                 col_ids,
                 init_model_fpath,
                 latest_model_fpath,
                 best_model_fpath,
                 rounds_to_train=256,
                 minimum_reporting=-1,
                 straggler_cutoff_time=np.inf,
                 disable_equality_check=True,
                 test_mode_whitelist=None,
                 compression_pipeline=None, 
                 **kwargs):
        self.logger = logging.getLogger(__name__)
        self.id = agg_id
        self.fed_id = fed_id
        #FIXME: Should we do anything to insure the intial model is compressed?
        self.model = load_proto(init_model_fpath)
        self.latest_model_fpath = latest_model_fpath
        self.best_model_fpath = best_model_fpath
        self.col_ids = col_ids
        self.round_num = 1
        self.rounds_to_train = rounds_to_train
        self.quit_job_sent_to = []
        self.disable_equality_check = disable_equality_check
        self.minimum_reporting = minimum_reporting
        self.straggler_cutoff_time = straggler_cutoff_time
        self.round_start_time = None
        self.test_mode_whitelist = test_mode_whitelist

        #FIXME: close the handler before termination.
        log_dir = './logs/tensorboardX/%s_%s' % (self.id, self.fed_id)
        self.tb_writer = tensorboardX.SummaryWriter(log_dir, flush_secs=10)

        self.model_update_in_progress_tensors = None

        self.init_per_col_round_stats()
        self.best_model_score = None
        self.mutex = Lock()

        self.compression_pipeline = compression_pipeline or NoCompressionPipeline()

    def valid_collaborator_CN_and_id(self, common_name, col_id):
        # if self.test_mode_whitelist is None, then the common_name must match col_id and be in col_ids
        if self.test_mode_whitelist is None:
            return common_name == col_id and col_id in self.col_ids
        # otherwise, common_name must be in whitelist and col_id must be in col_ids
        else:
            return common_name in self.test_mode_whitelist and col_id in self.col_ids

    def all_quit_jobs_sent(self):
        return sorted(self.quit_job_sent_to) == sorted(self.col_ids)

    def validate_header(self, message):
        # validate that the message is for me
        check_equal(message.header.recipient, self.id, self.logger)
        
        # validate that the message is for my federation
        check_equal(message.header.federation_id, self.fed_id, self.logger)
        
        # validate that the sender is one of my collaborators
        check_is_in(message.header.sender, self.col_ids, self.logger)

    def init_per_col_round_stats(self):
        """Initalize the metrics from collaborators for each round of aggregation. """
        keys = ["loss_results", "collaborator_training_sizes", "agg_validation_results", "preagg_validation_results", "collaborator_validation_sizes"]
        values = [{} for i in range(len(keys))]
        self.per_col_round_stats = dict(zip(keys, values))

    def collaborator_is_done(self, c):
        assert c in self.col_ids

        # FIXME: this only works because we have fixed roles each round
        return (c in self.per_col_round_stats["loss_results"] and
                c in self.per_col_round_stats["collaborator_training_sizes"] and
                c in self.per_col_round_stats["agg_validation_results"] and
                c in self.per_col_round_stats["preagg_validation_results"] and
                c in self.per_col_round_stats["collaborator_validation_sizes"])

    def num_collaborators_done(self):
        return sum([self.collaborator_is_done(c) for c in self.col_ids])

    def straggler_time_expired(self):
        return self.round_start_time is not None and ((time.time() - self.round_start_time) > self.straggler_cutoff_time)

    def minimum_collaborators_reported(self):
        return self.num_collaborators_done() >= self.minimum_reporting

    def straggler_cutoff_check(self):
        cutoff = self.straggler_time_expired() and self.minimum_collaborators_reported()
        if cutoff:
            collaborators_done = [c for c in self.col_ids if self.collaborator_is_done(c)]
            self.logger.info('\tEnding round early due to straggler cutoff. Collaborators done: {}'.format(collaborators_done))
        return cutoff
    
    def end_of_round_check(self):
        # FIXME: find a nice, clean way to manage these values without having to manually ensure
        # the keys are in sync

        # assert our dictionary keys are in sync
        check_equal(self.per_col_round_stats["loss_results"].keys(), self.per_col_round_stats["collaborator_training_sizes"].keys(), self.logger)
        check_equal(self.per_col_round_stats["agg_validation_results"].keys(), self.per_col_round_stats["collaborator_validation_sizes"].keys(), self.logger)

        # if everyone is done OR our straggler policy calls for an early round end
        if self.num_collaborators_done() == len(self.col_ids) or self.straggler_cutoff_check():
            self.end_of_round()

    def get_weighted_average_of_collaborators(self, value_dict, weight_dict):
        cols = [k for k in value_dict.keys() if k in self.col_ids]
        return np.average([value_dict[c] for c in cols], weights=[weight_dict[c] for c in cols])        

    def end_of_round(self):
        # FIXME: what all should we do to track results/metrics? It should really be an easy, extensible solution

        # compute the weighted loss average
        round_loss = self.get_weighted_average_of_collaborators(self.per_col_round_stats["loss_results"],
                                                                self.per_col_round_stats["collaborator_training_sizes"])

        # compute the weighted validation average
        round_val = self.get_weighted_average_of_collaborators(self.per_col_round_stats["agg_validation_results"],
                                                                self.per_col_round_stats["collaborator_validation_sizes"])

        # FIXME: proper logging
        self.logger.info('round results for model id/version {}/{}'.format(self.model.header.id, self.model.header.version))
        self.logger.info('\tvalidation: {}'.format(round_val))
        self.logger.info('\tloss: {}'.format(round_loss))

        self.tb_writer.add_scalars('training/loss', {**self.per_col_round_stats["loss_results"], "federation": round_loss}, global_step=self.round_num)
        self.tb_writer.add_scalars('training/size', self.per_col_round_stats["collaborator_training_sizes"], global_step=self.round_num)
        self.tb_writer.add_scalars('validation/preagg_result', self.per_col_round_stats["preagg_validation_results"], global_step=self.round_num)
        self.tb_writer.add_scalars('validation/size', self.per_col_round_stats["collaborator_validation_sizes"], global_step=self.round_num-1)
        self.tb_writer.add_scalars('validation/agg_result', {**self.per_col_round_stats["agg_validation_results"], "federation": round_val}, global_step=self.round_num-1)

        # construct the model protobuf from in progress tensors (with incremented version number)
        self.model = construct_proto(tensor_dict=self.model_update_in_progress_tensors, 
                                     model_id=self.model.header.id, 
                                     model_version=self.model.header.version + 1, 
                                     compression_pipeline=self.compression_pipeline)
        
        # Save the new model as latest model.
        dump_proto(self.model, self.latest_model_fpath)

        model_score = round_val
        if self.best_model_score is None or self.best_model_score < model_score:
            self.logger.info("Saved the best model with score {:f}.".format(model_score))
            self.best_model_score = model_score
            # Save a model proto version to file as current best model.
            dump_proto(self.model, self.best_model_fpath)

        # clear the update pointer
        self.model_update_in_progress_tensors = None

        self.init_per_col_round_stats()

        self.round_num += 1
        self.logger.debug("Start a new round %d." % self.round_num)
        self.round_start_time = None

    def UploadLocalModelUpdate(self, message):
        self.mutex.acquire(blocking=True)
        try:
            t = time.time()
            self.validate_header(message)

            self.logger.info("Receive model update from %s " % message.header.sender)

            # Get the model parameters from the model proto
            model_tensors = deconstruct_proto(model_proto=message.model, compression_pipeline=self.compression_pipeline)

            # validate this model header
            check_equal(message.model.header.id, self.model.header.id, self.logger)
            check_equal(message.model.header.version, self.model.header.version, self.logger)

            # ensure we haven't received an update from this collaborator already
            check_not_in(message.header.sender, self.per_col_round_stats["loss_results"], self.logger)
            check_not_in(message.header.sender, self.per_col_round_stats["collaborator_training_sizes"], self.logger)

            # if this is our very first update for the round, we take these model tensors as-is
            # FIXME: move to model deltas, add with original to reconstruct
            # FIXME: this really only works with a trusted collaborator. Sanity check this against self.model
            if self.model_update_in_progress_tensors is None:
                self.model_update_in_progress_tensors = model_tensors

            # otherwise, we compute the streaming weighted average
            else:
                # get the current update size total
                total_update_size = np.sum(list(self.per_col_round_stats["collaborator_training_sizes"].values()))

                # compute the weights for the global vs local tensors for our streaming average
                weight_g = total_update_size / (message.data_size + total_update_size)
                weight_l = message.data_size / (message.data_size + total_update_size)

                # The model parameters are represented in float32 and will be transmitted in byte stream.
                weight_g = weight_g.astype(np.float32)
                weight_l = weight_l.astype(np.float32)

                # FIXME: right now we're really using names just to sanity check consistent ordering

                # check that the models include the same number of tensors
                check_equal(len(self.model_update_in_progress_tensors), len(model_tensors), self.logger)

                # aggregate all the model tensors in the tensor_dict 
                # (weighted average of local update l and global tensor g for all l, g)
                for name, l in model_tensors.items():
                    g = self.model_update_in_progress_tensors[name]
                    # check that g and l have the same shape
                    check_equal(g.shape, l.shape, self.logger)
                    
                    # sanity check that the tensors are indeed different for non opt tensors 
                    # TODO: modify this to better comprehend for non pytorch how to identify the opt portion (use model opt info?)               
                    if (not self.disable_equality_check \
                        and not name.startswith('__opt') \
                        and 'RMSprop' not in name \
                        and 'Adam' not in name \
                        and 'RMSProp' not in name):
                        check_equal(np.all(g == l), False, self.logger)
                        
                    
                    # now store a weighted average into the update in progress
                    self.model_update_in_progress_tensors[name] = np.average([g, l], weights=[weight_g, weight_l], axis=0)

            # store the loss results and training update size
            self.per_col_round_stats["loss_results"][message.header.sender] = message.loss
            self.per_col_round_stats["collaborator_training_sizes"][message.header.sender] = message.data_size

            # return LocalModelUpdateAck
            self.logger.debug("Complete model update from %s " % message.header.sender)
            reply = LocalModelUpdateAck(header=self.create_reply_header(message))

            self.end_of_round_check()

            self.logger.debug('aggregator handled UploadLocalModelUpdate in time {}'.format(time.time() - t))
        finally:
            self.mutex.release()

        return reply

    def UploadLocalMetricsUpdate(self, message):
        self.mutex.acquire(blocking=True)
        try:
            t = time.time()
            self.validate_header(message)

            self.logger.debug("Receive local validation results from %s " % message.header.sender)
            model_header = message.model_header

            # validate this model header
            check_equal(model_header.id, self.model.header.id, self.logger)
            check_equal(model_header.version, self.model.header.version, self.logger)
            
            sender = message.header.sender

            if sender not in self.per_col_round_stats["agg_validation_results"]:
                # Pre-train validation
                # ensure we haven't received an update from this collaborator already
                # FIXME: is this an error case that should be handled?
                check_not_in(message.header.sender, self.per_col_round_stats["agg_validation_results"], self.logger)
                check_not_in(message.header.sender, self.per_col_round_stats["collaborator_validation_sizes"], self.logger)
                
                # store the validation results and validation size
                self.per_col_round_stats["agg_validation_results"][message.header.sender] = message.results
                self.per_col_round_stats["collaborator_validation_sizes"][message.header.sender] = message.data_size
            elif sender not in self.per_col_round_stats["preagg_validation_results"]:
                # Post-train validation
                check_not_in(message.header.sender, self.per_col_round_stats["preagg_validation_results"], self.logger)
                self.per_col_round_stats["preagg_validation_results"][message.header.sender] = message.results

            reply = LocalValidationResultsAck(header=self.create_reply_header(message))

            self.end_of_round_check()

            self.logger.debug('aggregator handled UploadLocalMetricsUpdate in time {}'.format(time.time() - t))
        finally:
            self.mutex.release()

        self.logger.debug('aggregator handled UploadLocalMetricsUpdate in time {}'.format(time.time() - t))

        return reply

    def RequestJob(self, message):
        t = time.time()
        self.validate_header(message)

        # FIXME: we should really have each collaborator validate one last time
        # check if we are done
        if self.round_num > self.rounds_to_train:
            job = JOB_QUIT
            self.quit_job_sent_to.append(message.header.sender)
        # FIXME: this flow needs to depend on a job selection output for the round
        # for now, all jobs require and in-sync model, so it is the first check
        # check if the sender model is out of date
        elif self.collaborator_out_of_date(message.model_header):
            job = JOB_DOWNLOAD_MODEL
        # else, check if this collaborator has not sent validation results
        elif message.header.sender not in self.per_col_round_stats["agg_validation_results"]:
            job = JOB_VALIDATE
        # else, check if this collaborator has not sent training results
        elif message.header.sender not in self.per_col_round_stats["collaborator_training_sizes"]:
            job = JOB_TRAIN
        elif message.header.sender not in self.per_col_round_stats["preagg_validation_results"]:
            job = JOB_VALIDATE
        # else this collaborator is done for the round
        else:
            job = JOB_YIELD
        
        self.logger.debug("Receive job request from %s and assign with %s" % (message.header.sender, job))

        reply = JobReply(header=self.create_reply_header(message), job=job)

        if reply.job is not JOB_YIELD:
            # check to see if we need to set our round start time
            self.mutex.acquire(blocking=True)
            try:
                if self.round_start_time is None:
                    self.round_start_time = time.time()
            finally:
                self.mutex.release()

            self.logger.debug('aggregator handled RequestJob in time {}'.format(time.time() - t))
        elif self.straggler_cutoff_time != np.inf:
            # we have an idle collaborator and a straggler cutoff time, so we should check for early round end
            self.mutex.acquire(blocking=True)
            try:
                self.end_of_round_check()
            finally:
                self.mutex.release()
        
        return reply      

    def DownloadModel(self, message):
        t = time.time()
        self.validate_header(message)

        self.logger.info("Received model download request from %s " % message.header.sender)

        # check if the models don't match
        if not(self.collaborator_out_of_date(message.model_header)):
            statement = "Assertion failed: self.collaborator_out_of_date(message.model_header)"
            self.logger.exception(statement)
            raise RuntimeError(statement)

        reply = GlobalModelUpdate(header=self.create_reply_header(message), model=self.model)

        self.logger.debug('aggregator handled RequestJob in time {}'.format(time.time() - t))
        
        return reply       

    def create_reply_header(self, message):
        return MessageHeader(sender=self.id, recipient=message.header.sender, federation_id=self.fed_id, counter=message.header.counter)

    def collaborator_out_of_date(self, model_header):
        # validate that this is the right model to be checking
        check_equal(model_header.id, self.model.header.id, self.logger)
        
        return model_header.version != self.model.header.version
