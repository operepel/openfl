# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import numpy as np
import pandas as pd
import tensorboardX
import logging

from .. import check_equal, check_not_equal, check_is_in, check_not_in
from ..proto.collaborator_aggregator_interface_pb2 import MessageHeader, MetadataProto, ModelProto
from ..proto.collaborator_aggregator_interface_pb2 import TasksRequest, TasksResponse, TensorRequest, TensorResponse, NamedTensor, Acknowledgement
from tfedlrn import TensorKey,TaskResultKey
from tfedlrn.tensor_transformation_pipelines import NoCompressionPipeline, TensorCodec
from tfedlrn.tensor_db import TensorDB

from tfedlrn.proto.protoutils import load_proto, dump_proto, construct_proto, deconstruct_proto, construct_named_tensor, construct_model_proto, deconstruct_model_proto

class Aggregator(object):

    """An Aggregator is the central node in federated learning

    Parameters
    ----------
    aggregator_uuid : str
        Aggregation ID.
    federation_uuid : str
        Federation ID.
    collaborator_common_names : list of str
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

    def __init__(self,
                 aggregator_uuid,
                 federation_uuid,
                 collaborator_common_names,
                 initial_model_fpath,
                 latest_model_fpath,
                 best_model_fpath,
                 custom_tensor_dir,
                 task_assigner,
                 rounds_to_train=256,
                 minimum_reporting=-1,
                 straggler_cutoff_time=np.inf,
                 disable_equality_check=True,
                 single_col_cert_common_name=None,
                 compression_pipeline=None,
                 **kwargs):
        self.round_number = 0
        self.single_col_cert_common_name = single_col_cert_common_name
        self.logger = logging.getLogger(__name__)

        if self.single_col_cert_common_name is not None:
            self.log_big_warning()
        else:
            self.single_col_cert_common_name = '' # FIXME: '' instead of None is just for protobuf compatibility. Cleaner solution?

        self.rounds_to_train = rounds_to_train
        #If the collaborator requests a delta, this value is set to true
        self.collaborator_common_names = collaborator_common_names
        self.uuid = aggregator_uuid
        self.federation_uuid = federation_uuid
        self.task_assigner = task_assigner
        self.quit_job_sent_to = []
        self.tensor_db = TensorDB()
        self.compression_pipeline = compression_pipeline or NoCompressionPipeline() 
        self.tensor_codec = TensorCodec(self.compression_pipeline)
        self.initial_model_fpath = initial_model_fpath
        self.best_model_fpath = best_model_fpath
        self.latest_model_fpath = latest_model_fpath
        self.best_model_score = None
        self.custom_tensor_dir = custom_tensor_dir
        self.load_initial_tensors() # keys are TensorKeys
        log_dir = './logs/tensorboardX/{}_{}'.format(self.uuid,self.federation_uuid)
        self.tb_writer = tensorboardX.SummaryWriter(log_dir, flush_secs=10)

        self.collaborator_tensor_results = {} # {TensorKey: nparray}}

        # these enable getting all tensors for a task
        self.collaborator_tasks_results = {} # {TaskResultKey: list of TensorKeys}
        self.collaborator_task_weight = {} # {TaskResultKey: data_size}

    def load_initial_tensors(self):
        """
        Load all of the tensors required to begin federated learning:

        1. Initial model
        2. Any custom tensors. These are previously serialized named tensors

        Parameters
        ----------
        """
        #If the collaborator requests a delta, this value is set to true
        self.model = load_proto(self.initial_model_fpath)
        tensor_dict,round_number = deconstruct_model_proto(self.model,compression_pipeline=self.compression_pipeline)
        if round_number > self.round_number:
            self.logger.info('Starting training from round {} of previously saved model'.format(round_number))
            self.round_number = round_number
        tensor_key_dict = {TensorKey(k,self.uuid,self.round_number,False,('model',)):v for k,v in tensor_dict.items()}
        #All initial model tensors are loaded here
        self.tensor_db.cache_tensor(tensor_key_dict)
        self.logger.debug('This is the initial tensor_db: {}'.format(self.tensor_db))
        if self.custom_tensor_dir != None:
            #Here is where the additional tensors should be loaded into the TensorDB
            pass

    def save_model(self,round_number,file_path):
        """
        Save the best or latest model

        Params
        ------
        round_number:   Model round to be saved
        file_path:      Either the best model or latest model file path

        Returns
        -------
        None
        """
        #Extract the model from TensorDB and set it to the new model
        og_tensor_dict,_ = deconstruct_model_proto(self.model,compression_pipeline=self.compression_pipeline)
        tensor_keys = [TensorKey(k,self.uuid,round_number,False,('model',)) for k,v in og_tensor_dict.items()]
        best_tensor_dict = {}
        for tk in tensor_keys:
            tk_name,_,_,_,_ = tk
            best_tensor_dict[tk_name] = self.tensor_db.get_tensor_from_cache(tk)
        self.model = construct_model_proto(best_tensor_dict,round_number,self.compression_pipeline)
        dump_proto(self.model, file_path)


    def valid_collaborator_CN_and_id(self, cert_common_name, collaborator_common_name):
        """Determine if the collaborator certificate and ID are valid for this federation.

        Args:
            cert_common_name: Common name for security certificate
            collaborator_common_name: Common name for collaborator

        Returns:
            bool: True means the collaborator common name matches the name in the security certificate.

        """
        # if self.test_mode_whitelist is None, then the common_name must match collaborator_common_name and be in collaborator_common_names
        if self.single_col_cert_common_name == '':  # FIXME: '' instead of None is just for protobuf compatibility. Cleaner solution?
            return cert_common_name == collaborator_common_name and collaborator_common_name in self.collaborator_common_names
        # otherwise, common_name must be in whitelist and collaborator_common_name must be in collaborator_common_names
        else:
            return cert_common_name == self.single_col_cert_common_name and collaborator_common_name in self.collaborator_common_names


    def all_quit_jobs_sent(self):
        return set(self.quit_job_sent_to) == set(self.collaborator_common_names)

    def check_request(self, request):
        """
        Validate request header matches expected values
        """
        #TODO improve this check. The sender name could be spoofed
        check_is_in(request.header.sender, self.collaborator_common_names, self.logger) 

        #Validate the message is for me
        check_equal(request.header.receiver, self.uuid, self.logger)

        #Validate message is for my federation
        check_equal(request.header.federation_uuid, self.federation_uuid, self.logger)

        #Check that we agree on the single cert common name
        check_equal(request.header.single_col_cert_common_name, self.single_col_cert_common_name, self.logger)


    def get_header(self,collaborator_name):
        """
        Compose and return MessageHeader
        """
        return MessageHeader(sender=self.uuid, receiver=collaborator_name, federation_uuid=self.federation_uuid, single_col_cert_common_name=self.single_col_cert_common_name)

    def get_sleep_time(self):
        """
        Sleep 10 seconds
        """
        return 10

    def time_to_quit(self):
        """
        If all rounds are complete, it's time to quit
        """
        if self.round_number >= self.rounds_to_train:
            return True
        return False
        
    def GetTasks(self, request):
        # all messages get sanity checked
        self.check_request(request)

        collaborator_name = request.header.sender

        # first, if it is time to quit, inform the collaborator
        if self.time_to_quit():
            self.logger.info('Sending signal to collaborator {} to shutdown...'.format(collaborator_name))
            self.quit_job_sent_to.append(collaborator_name)
            return TasksResponse(header=self.get_header(collaborator_name),
                                 round_number=self.round_number,
                                 tasks=None,
                                 sleep_time=0,
                                 quit=True)
        
        # otherwise, get the tasks from our task assigner
        tasks = self.task_assigner.get_tasks_for_collaborator(collaborator_name,self.round_number) # fancy task assigners may want aggregator state
        
        # if no tasks, tell the collaborator to sleep
        if len(tasks) == 0:
            return TasksResponse(header=self.get_header(collaborator_name),
                                 round_number=self.round_number,
                                 tasks=None,
                                 sleep_time=self.get_sleep_time(), # this could be an extensible function if we want
                                 quit=False)

        # if we do have tasks, remove any that we already have results for
        tasks = [t for t in tasks if not self.collaborator_task_completed(collaborator_name, t, self.round_number)]

        #Do the check again because it's possible that all tasks have been completed
        if len(tasks) == 0:
            return TasksResponse(header=self.get_header(collaborator_name),
                                 round_number=self.round_number,
                                 tasks=None,
                                 sleep_time=self.get_sleep_time(), # this could be an extensible function if we want
                                 quit=False)

        self.logger.info('Sending tasks to collaborator {} for round {}'.format(collaborator_name,self.round_number))
        return TasksResponse(header=self.get_header(collaborator_name),
                             round_number=self.round_number,
                             tasks=tasks,
                             sleep_time=0,
                             quit=False)

    def GetAggregatedTensor(self, request):
        # all messages get sanity checked
        self.check_request(request)

        # get the values we need from the protobuf
        collaborator_name   = request.header.sender
        tensor_name         = request.tensor_name
        require_lossless    = request.require_lossless
        round_number        = request.round_number
        report              = request.report
        tags                = request.tags

        self.logger.debug('Retrieving aggregated tensor {} for collaborator {}'.format(tensor_name,collaborator_name))

        if 'compressed' in tags or require_lossless:
            compress_lossless=True

        #TODO the TensorDB doesn't support compressed data yet. The returned tensor will
        #be recompressed anyway.
        if 'compressed' in tags:
            tags.remove('compressed')

        tensor_key = TensorKey(tensor_name, self.uuid, round_number, report, tuple(tags))
        tensor_name,origin,round_number, report, tags = tensor_key

        send_model_deltas = False
        compress_lossless = False


        if 'aggregated' in tags and 'delta' in tags and round_number != 0:
            send_model_deltas = True
            agg_tensor_key = TensorKey(tensor_name,origin,round_number,report,('aggregated',))
        else:
            agg_tensor_key = tensor_key
        
        nparray = self.tensor_db.get_tensor_from_cache(tensor_key)

        if nparray is None:
            raise ValueError("Aggregator does not have an aggregated tensor for {}".format(tensor_key))

        # quite a bit happens in here, including compression, delta handling, etc...
        # we might want to cache these as well
        named_tensor = self.nparray_to_named_tensor(agg_tensor_key,nparray,send_model_deltas=True,compress_lossless=compress_lossless)

        return TensorResponse(header=self.get_header(collaborator_name),
                              round_number=round_number,
                              tensor=named_tensor)

    def nparray_to_named_tensor(self,tensor_key, nparray,send_model_deltas,compress_lossless):
        """
        This function constructs the NamedTensor Protobuf and also includes logic to create delta, 
        compress tensors with the TensorCodec, etc.
        """

        # if we have an aggregated tensor, we can make a delta
        tensor_name,origin,round_number,report,tags = tensor_key
        if('aggregated' in tags and send_model_deltas):
          #Should get the pretrained model to create the delta. If training has happened,
          #Model should already be stored in the TensorDB
          model_nparray = self.tensor_db.get_tensor_from_cache(TensorKey(tensor_name,\
                                                                  origin,\
                                                                  round_number-1,\
                                                                  report,\
                                                                  ('model',))) 
        
          assert(model_nparray != None), "The original model layer should be present if the latest aggregated model is present"
          delta_tensor_key, delta_nparray = self.tensor_codec.generate_delta(tensor_key,nparray,model_nparray)
          delta_comp_tensor_key,delta_comp_nparray,metadata = \
                  self.tensor_codec.compress(delta_tensor_key,delta_nparray,lossless=compress_lossless)
          named_tensor = construct_named_tensor(delta_comp_tensor_key,delta_comp_nparray,metadata,lossless=compress_lossless)

        else:
            #Assume every other tensor requires lossless compression
            compressed_tensor_key, compressed_nparray, metadata = \
                    self.tensor_codec.compress(tensorkey,nparray,require_lossless=True)
            named_tensor = construct_named_tensor(compressed_tensor_key,compressed_nparray,metadata,lossless=compress_lossless)
        
        return named_tensor



    def collaborator_task_completed(self, collaborator, task, round_num):
        """
        Check if the collaborator has completed the task for the round. 
        The aggregator doesn't actually know which tensors should be sent from the collaborator
        so it must to rely specifically on the presence of previous results

        Parameters
        ----------
        collaborator
        task_name
        round_number

        Returns
        -------
        bool

        """
        task_key = TaskResultKey(task, collaborator, round_num)
        return task_key in self.collaborator_tasks_results


    def SendLocalTaskResults(self, request):
        # all messages get sanity checked
        self.check_request(request)

        # get the values we need from the protobuf
        collaborator_name   = request.header.sender
        task_name           = request.task_name
        round_number        = request.round_number
        data_size           = request.data_size
        named_tensors       = request.tensors
        
        self.logger.info('Collaborator {} is sending task results for {}, round {}'.format(collaborator_name,task_name,round_number))

        # TODO: do we drop these on the floor?
        # if round_number != self.round_number:
        #     return Acknowledgement(header=self.get_header(collaborator_name))

        task_key = TaskResultKey(task_name, collaborator_name, round_number)

        # we mustn't have results already
        if self.collaborator_task_completed(collaborator_name, task_name, round_number):
            raise ValueError("Aggregator already has task results from collaborator {} for task {}".format(collaborator_name, task_key))

        # initialize the list of tensors that go with this task
        #Setting these incrementally is leading to missing values
        #self.collaborator_tasks_results[task_key] = []
        task_results = []

        # go through the tensors and add them to the tensor dictionary and the task dictionary
        for named_tensor in named_tensors:
            # sanity check that this tensor has been updated
            if named_tensor.round_number != round_number:
                raise ValueError('Collaborator {} is reporting results for the wrong round. Exiting...'.format(collaborator_name))

            # quite a bit happens in here, including decompression, delta handling, etc...
            tensor_key, nparray = self.process_named_tensor(named_tensor,collaborator_name)

            task_results.append(tensor_key)
            #By giving task_key it's own weight, we can support different training/validation weights
            #As well as eventually supporting weights that change by round (if more data is added)
            self.collaborator_task_weight[task_key] = data_size

        self.collaborator_tasks_results[task_key] = task_results
        
        self.end_of_task_check(task_name)

        return Acknowledgement(header=self.get_header(collaborator_name))


    def process_named_tensor(self,named_tensor,collaborator_name):
        """
        Extract the named tensor fields, performs decompression, delta computation, 
        and inserts results into TensorDB.

        Parameters
        ----------
        named_tensor:       NamedTensor protobuf that will be extracted from and processed
        collaborator_name:  Collaborator name is needed for proper tagging of resulting tensorkeys  
        """
        raw_bytes = named_tensor.data_bytes
        metadata = [{'int_to_float': proto.int_to_float,
                     'int_list': proto.int_list,
                     'bool_list': proto.bool_list} for proto in named_tensor.transformer_metadata]
        #The tensor has already been transfered to aggregator, so the newly constructed tensor should have the aggregator origin
        tensor_key = TensorKey(named_tensor.name, self.uuid, named_tensor.round_number, named_tensor.report, tuple(named_tensor.tags))
        tensor_name,origin,round_number,report,tags = tensor_key
        assert('compressed' in tags or 'lossy_decompressed' in tags), 'Named tensor {} is not compressed'.format(tensor_key)
        if 'compressed' in tags:
            dec_tk, decompressed_nparray =  \
                    self.tensor_codec.decompress(tensor_key,data=raw_bytes,transformer_metadata=metadata,require_lossless=True)
            dec_name,dec_origin,dec_round_num,dec_report,dec_tags = dec_tk
            #Need to add the collaborator tag to the resulting tensor
            if type(dec_tags) == str:
                new_tags = tuple([dec_tags] + [collaborator_name])
            else:
                new_tags = tuple(list(dec_tags) + [collaborator_name])
            #layer.agg.n.trained.delta.col_i
            decompressed_tensor_key = TensorKey(dec_name,dec_origin,dec_round_num,dec_report,new_tags)
        if 'lossy_compressed' in tags:
            dec_tk, decompressed_nparray =  \
                    self.tensor_codec.decompress(tensor_key,data=raw_bytes,transformer_metadata=metadata)
            dec_name,dec_origin,dec_round_num,dec_report,dec_tags = dec_tk
            if type(dec_tags) == str:
                new_tags = tuple([dec_tags] + [collaborator_name])
            else:
                new_tags = tuple(list(dec_tags) + [collaborator_name])
            #layer.agg.n.trained.delta.lossy_decompressed.col_i
            decompressed_tensor_key = TensorKey(dec_name,dec_origin,dec_round_num,dec_report,new_tags)

        if 'delta' in tags:
            base_model_tensor_key = TensorKey(tensor_name,origin,round_number,report,('model',))
            base_model_nparray = self.tensor_db.get_tensor_from_cache(base_model_tensor_key)
            if base_model_nparray is None:
                raise ValueError('Base model {} not present in TensorDB'.format(base_model_tensor_key))
            final_tensor_key,final_nparray = self.tensor_codec.apply_delta(decompressed_tensor_key,decompressed_nparray,base_model_nparray)
        else:
            final_tensor_key = decompressed_tensor_key
            final_nparray = decompressed_nparray


        assert(final_nparray is not None), 'Could not create tensorkey {}'.format(final_tensor_key)
        self.tensor_db.cache_tensor({final_tensor_key: final_nparray})
        self.logger.debug('Created TensorKey: {}'.format(final_tensor_key))
        
        return final_tensor_key, final_nparray

    def nparray_to_named_tensor(self,tensor_key, nparray,send_model_deltas,compress_lossless):
        """
        This function constructs the NamedTensor Protobuf and also includes logic to create delta, 
        compress tensors with the TensorCodec, etc.
        """

        tensor_name,origin,round_number,report,tags = tensor_key
        # if we have an aggregated tensor, we can make a delta
        if('aggregated' in tensor_name and send_model_deltas):
          #Should get the pretrained model to create the delta. If training has happened,
          #Model should already be stored in the TensorDB
          model_nparray = self.tensor_db.get_tensor_from_cache(TensorKey(tensor_name,\
                                                                  origin,\
                                                                  round_number-1,\
                                                                  ('model',))) 
        
          assert(model_nparray is not None), "The original model layer should be present if the latest aggregated model is present"
          delta_tensor_key, delta_nparray = self.tensor_codec.generate_delta(tensor_key,nparray,model_nparray)
          delta_comp_tensor_key,delta_comp_nparray,metadata = \
                  self.tensor_codec.compress(delta_tensor_key,delta_nparray,lossless=compress_lossless)
          named_tensor = construct_named_tensor(delta_comp_tensor_key,delta_comp_nparray,metadata,lossless=compress_lossless)

        else:
            #Assume every other tensor requires lossless compression
            compressed_tensor_key, compressed_nparray, metadata = \
                    self.tensor_codec.compress(tensor_key,nparray,require_lossless=True)
            named_tensor = construct_named_tensor(compressed_tensor_key,compressed_nparray,metadata,lossless=compress_lossless)
        
        return named_tensor


    def end_of_task_check(self, task_name):
        if self.is_task_done(task_name):
            # now check for the end of the round
            self.end_of_round_check()

    def end_of_round_check(self):
        if self.is_round_done():
            #Compute all validation related metrics
            all_tasks = self.task_assigner.get_all_tasks_for_round(self.round_number)
            for task_name in all_tasks:
                self.logger.info('{} task metrics...'.format(task_name))
                #By default, print out all of the metrics that the validation task sent
                #This handles getting the subset of collaborators that may be part of the validation task
                collaborators_for_task = self.task_assigner.get_collaborators_for_task(task_name,self.round_number)
                #The collaborator data sizes for that task
                collaborator_weights_unnormalized = \
                        {c:self.collaborator_task_weight[TaskResultKey(task_name,c,self.round_number)] \
                        for c in collaborators_for_task}
                weight_total = sum(collaborator_weights_unnormalized.values())
                collaborator_weight_dict = {k:v/weight_total for k,v in collaborator_weights_unnormalized.items()}
                
                #The validation task should have just a couple tensors (i.e. metrics) associated with it.
                #Because each collaborator should have sent the same tensor list, we can use the first 
                #collaborator in our subset, and apply the correct transformations to the tensorkey to 
                #resolve the aggregated tensor for that round
                task_key = TaskResultKey(task_name,collaborators_for_task[0],self.round_number)
                for tensor_key in self.collaborator_tasks_results[task_key]:
                    tensor_name,origin,round_number,report,tags = tensor_key
                    assert(tags[-1] == collaborators_for_task[0]), \
                            'Tensor {} in task {} has not been processed correctly'.format(tensor_key,task_name)
                    #Strip the collaborator label, and lookup aggregated tensor
                    new_tags = tuple(list(tags[:-1]))
                    agg_tensor_key = TensorKey(tensor_name,origin,round_number,report,new_tags)
                    agg_tensor_name,agg_origin,agg_round_number,agg_report,agg_tags = agg_tensor_key
                    agg_results = self.tensor_db.get_aggregated_tensor(agg_tensor_key,collaborator_weight_dict)
                    if report:
                        #Print the aggregated metric
                        if agg_results is None:
                            self.logger.warning('Aggregated metric {} could not be collect for round {}. Skipping reporting for this round'.format(agg_tensor_name,self.round_number))
                        self.logger.info('{0}:\t{1:.4f}'.format(agg_tensor_name,agg_results))
                        #TODO Add all of the logic for saving the model based on best accuracy, lowest loss, etc.
                        if 'validate_agg' in tags:
                            #Compare the accuracy of the model, and potentially save it
                            if self.best_model_score is None or self.best_model_score < agg_results:
                                self.logger.info('Saved the best model with score {:f}'.format(agg_results))
                                self.best_model_score = agg_results
                                self.save_model(round_number,self.best_model_fpath)
                    if 'trained' in tags:
                        #The aggregated tensorkey tags should have the form of 'trained' or 'trained.lossy_decompressed'
                        #They need to be relabeled to 'aggregated' and reinserted. Then delta performed, 
                        #compressed, etc. then reinserted to TensorDB with 'model' tag

                        #First insert the aggregated model layer with the correct tensorkey
                        agg_tag_tk = TensorKey(tensor_name,origin,round_number+1,report,('aggregated',))
                        self.tensor_db.cache_tensor({agg_tag_tk:agg_results})

                        #Create delta and save it in TensorDB
                        base_model_tk = TensorKey(tensor_name,origin,round_number,report,('model',))
                        base_model_nparray = self.tensor_db.get_tensor_from_cache(base_model_tk)
                        if base_model_nparray is not None:
                            delta_tk,delta_nparray = self.tensor_codec.generate_delta(agg_tag_tk,agg_results,base_model_nparray)
                            self.tensor_db.cache_tensor({delta_tk:delta_nparray})
                        else:
                            #This condition is possible for base model optimizer states (i.e. Adam/iter:0, SGD, etc.)
                            #These values couldn't be present for the base model because no training occurs on the aggregator
                            delta_tk,delta_nparray = agg_tag_tk,agg_results

                        #Compress lossless/lossy
                        compressed_delta_tk,compressed_delta_nparray,metadata = \
                                self.tensor_codec.compress(delta_tk,delta_nparray)

                        #TODO extend the TensorDB so that compressed data is supported. Once that is in place
                        #the compressed delta can just be stored here instead of recreating it for every request

                        #Decompress lossless/lossy
                        decompressed_delta_tk,decompressed_delta_nparray = \
                                self.tensor_codec.decompress(compressed_delta_tk,compressed_delta_nparray,metadata)

                        #Apply delta (unless delta couldn't be created)
                        if base_model_nparray is not None:
                            new_model_tk,new_model_nparray = \
                                    self.tensor_codec.apply_delta(decompressed_delta_tk,decompressed_delta_nparray,base_model_nparray)
                        else:
                            new_model_tk,new_model_nparray = decompressed_delta_tk, decompressed_delta_nparray

                        #Now that the model has been compressed/decompressed with delta operations,
                        #Relabel the tags to 'model'
                        new_model_tensor_name,new_model_origin,new_model_round_number,new_model_report,new_model_tags = new_model_tk
                        final_model_tk = TensorKey(new_model_tensor_name,new_model_origin,new_model_round_number,new_model_report,('model',))

                        #Finally, cache the updated model tensor
                        self.tensor_db.cache_tensor({final_model_tk:new_model_nparray})
                        #self.logger.debug('TensorDB contents after training round {}: {}'.format(self.round_number,self.tensor_db))

           
            #Once all of the task results have been processed
            #Increment the round number
            self.round_number += 1
            
            #Save the latest model
            self.logger.info('Saving round {} model...'.format(self.round_number))
            self.save_model(self.round_number,self.latest_model_fpath)


            #TODO This needs to be fixed!
            if self.time_to_quit():
                self.logger.info('Experiment Completed. Cleaning up...')
            else:
                self.logger.info('Starting round {}...'.format(self.round_number))


    def is_task_done(self, task_name):
        collaborators_needed = self.task_assigner.get_collaborators_for_task(task_name, self.round_number)

        return all([self.collaborator_task_completed(c, task_name, self.round_number) for c in collaborators_needed])

    def is_round_done(self):
        tasks_for_round = self.task_assigner.get_all_tasks_for_round(self.round_number)

        return all([self.is_task_done(t) for t in tasks_for_round])

    def log_big_warning(self):
        self.logger.warning("\n{}\nYOU ARE RUNNING IN SINGLE COLLABORATOR CERT MODE! THIS IS NOT PROPER PKI AND SHOULD ONLY BE USED IN DEVELOPMENT SETTINGS!!!! YE HAVE BEEN WARNED!!!".format(the_dragon))


the_dragon = """                                                                                           
                                                                                           
 ,@@.@@+@@##@,@@@@.`@@#@+  *@@@@ #@##@  `@@#@# @@@@@   @@    @@@@` #@@@ :@@ `@#`@@@#.@     
  @@ #@ ,@ +. @@.@* #@ :`   @+*@ .@`+.   @@ *@::@`@@   @@#  @@  #`;@`.@@ @@@`@`#@* +:@`    
  @@@@@ ,@@@  @@@@  +@@+    @@@@ .@@@    @@ .@+:@@@:  .;+@` @@ ,;,#@` @@ @@@@@ ,@@@* @     
  @@ #@ ,@`*. @@.@@ #@ ,;  `@+,@#.@.*`   @@ ,@::@`@@` @@@@# @@`:@;*@+ @@ @`:@@`@ *@@ `     
 .@@`@@,+@+;@.@@ @@`@@;*@  ;@@#@:*@+;@  `@@;@@ #@**@+;@ `@@:`@@@@  @@@@.`@+ .@ +@+@*,@     
  `` ``     ` ``  .     `     `      `     `    `  .` `  ``   ``    ``   `       .   `     
                                                                                           
                                                                                           
                                                                                           
                                            .**                                            
                                      ;`  `****:                                           
                                     @**`*******                                           
                         ***        +***********;                                          
                        ,@***;` .*:,;************                                          
                        ;***********@@***********                                          
                        ;************************,                                         
                        `*************************                                         
                         *************************                                         
                         ,************************                                         
                          **#*********************                                         
                          *@****`     :**********;                                         
                          +**;          .********.                                         
                          ;*;            `*******#:                       `,:              
                                          ****@@@++::                ,,;***.               
                                          *@@@**;#;:         +:      **++*,                
                                          @***#@@@:          +*;     ,****                 
                                          @*@+****           ***`     ****,                
                                         ,@#******.  ,       ****     **;,**.              
                                         * ******** :,       ;*:*+    **  :,**             
                                        #  ********::      *,.*:**`   *      ,*;           
                                        .  *********:      .+,*:;*:   :      `:**          
                                       ;   :********:       ***::**   `       ` **         
                                       +   :****::***  ,    *;;::**`             :*        
                                      ``   .****::;**:::    *;::::*;              ;*       
                                      *     *****::***:.    **::::**               ;:      
                                      #     *****;:****     ;*::;***               ,*`     
                                      ;     ************`  ,**:****;               ::*     
                                      :     *************;:;*;*++:                   *.    
                                      :     *****************;*                      `*    
                                     `.    `*****************;  :                     *.   
                                     .`    .*+************+****;:                     :*   
                                     `.    :;+***********+******;`    :              .,*   
                                      ;    ::*+*******************. `::              .`:.  
                                      +    :::**********************;;:`                *  
                                      +    ,::;*************;:::*******.                *  
                                      #    `:::+*************:::;********  :,           *  
                                      @     :::***************;:;*********;:,           *  
                                      @     ::::******:*********************:         ,:*  
                                      @     .:::******:;*********************,         :*  
                                      #      :::******::******###@*******;;****        *,  
                                      #      .::;*****::*****#****@*****;:::***;  ``  **   
                                      *       ::;***********+*****+#******::*****,,,,**    
                                      :        :;***********#******#******************     
                                      .`       `;***********#******+****+************      
                                      `,        ***#**@**+***+*****+**************;`       
                                       ;         *++**#******#+****+`      `.,..           
                                       +         `@***#*******#****#                       
                                       +          +***@********+**+:                       
                                       *         .+**+;**;;;**;#**#                        
                                      ,`         ****@         +*+:                        
                                      #          +**+         :+**                         
                                      @         ;**+,       ,***+                          
                                      #      #@+****      *#****+                          
                                     `;     @+***+@      `#**+#++                          
                                     #      #*#@##,      .++:.,#                           
                                    `*      @#            +.                               
                                  @@@                                                      
                                 #`@                                                       
                                  ,                                                        """
