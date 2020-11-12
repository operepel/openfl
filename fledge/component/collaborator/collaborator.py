# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import pandas  as pd
import numpy   as np

from logging import getLogger
from enum    import Enum
from time    import sleep

from fledge.protocols import MessageHeader, MetadataProto, ModelProto, NamedTensor, Acknowledgement
from fledge.protocols import TasksRequest, TasksResponse, TensorRequest, TensorResponse, TaskResults
from fledge.protocols import construct_proto, deconstruct_proto, construct_named_tensor
from fledge.utilities import TensorKey, check_type, check_equal, check_not_equal, split_tensor_dict_for_holdouts
from fledge.pipelines import TensorCodec, NoCompressionPipeline
from fledge.databases import TensorDB

class OptTreatment(Enum):
    """
    Optimizer Methods
    """

    RESET = 1
    """
    RESET tells each collaborator to reset the optimizer state at the beginning of each round.
    """
    CONTINUE_LOCAL = 2
    """
    CONTINUE_LOCAL tells each collaborator to continue with the local optimizer state from the previous round.
    """
    CONTINUE_GLOBAL = 3
    """
    CONTINUE_GLOBAL tells each collaborator to continue with the federally averaged optimizer state from the previous round.
    """

class Collaborator(object):
    """
    The Collaborator object class

    Args:
        collaborator_name (string): The common name for the collaborator
        aggregator_uuid: The unique id for the client
        federation_uuid: The unique id for the federation
        model: The model
        opt_treatment (string): The optimizer state treatment (Defaults to "CONTINUE_GLOBAL", which is aggreagated state from previous round.)
        compression_pipeline: The compression pipeline (Defaults to None)
        num_batches_per_round (int): Number of batches per round (Defaults to None)
        delta_updates (bool): True = Only model delta gets sent. False = Whole model gets sent to collaborator. (Defaults to False)
        single_col_cert_common_name: (Defaults to None)
        **kwargs : Additional parameters to pass to collaborator object
    """

    def __init__(self, 
                 collaborator_name, 
                 aggregator_uuid, 
                 federation_uuid, 
                 client,
                 task_runner,
                 tensor_pipe,
                 task_config,
                 opt_treatment = OptTreatment.RESET,
                 delta_updates = False,
                 **kwargs):
        
        self.single_col_cert_common_name = None

        if  self.single_col_cert_common_name == None:
            self.single_col_cert_common_name  = '' # for protobuf compatibility
        # we would really want this as an object

        self.collaborator_name = collaborator_name
        self.aggregator_uuid   = aggregator_uuid
        self.federation_uuid   = federation_uuid

        self.tensor_pipe       = tensor_pipe or NoCompressionPipeline()
        self.tensor_codec      = TensorCodec(self.tensor_pipe)
        self.tensor_db         = TensorDB()

        self.task_runner       = task_runner
        self.delta_updates     = delta_updates

        self.client = client
        self.header = MessageHeader(sender          = collaborator_name,
                                    receiver        = aggregator_uuid,
                                    federation_uuid = federation_uuid,
                                    single_col_cert_common_name = self.single_col_cert_common_name)

        self.task_config = task_config
        
        self.logger = getLogger(__name__)

        # RESET/CONTINUE_LOCAL/CONTINUE_GLOBAL
        if hasattr(OptTreatment, opt_treatment):
            self.opt_treatment = OptTreatment[opt_treatment]
        else:
            self.logger.error("Unknown opt_treatment: %s." % opt_treatment)
            raise NotImplementedError("Unknown opt_treatment: %s." % opt_treatment)
        
        self.task_runner.set_optimizer_treatment(self.opt_treatment.name)

    def _with_opt_vars(self):
        """
        Determines optimizer operation to perform.

        Returns:
           bool: True means *CONTINUE_GLOBAL* method for optimizer.

        """
        if self.opt_treatment in (OptTreatment.CONTINUE_LOCAL, OptTreatment.RESET):
            self.logger.debug("Do not share the optimization variables.")
            return False
        elif self.opt_treatment == OptTreatment.CONTINUE_GLOBAL:
            self.logger.debug("Share the optimization variables.")
            return True

    def validate_response(self, reply):
      # check that the message was intended to go to this collaborator
        check_equal(reply.header.receiver, self.collaborator_name, self.logger)
        check_equal(reply.header.sender, self.aggregator_uuid, self.logger)

      # check that federation id matches
        check_equal(reply.header.federation_uuid, self.federation_uuid, self.logger)

      # check that there is aggrement on the single_col_cert_common_name
        check_equal(reply.header.single_col_cert_common_name, self.single_col_cert_common_name, self.logger)

    def run(self):

        while True:
            tasks = self.get_tasks()
            if  tasks.quit:
                break
            elif tasks.sleep_time > 0:
                sleep(tasks.sleep_time) # some sleep function
            else:
                self.logger.info('Received the following tasks: {}'.format(tasks.tasks))
                for task in tasks.tasks:
                    self.do_task(task, tasks.round_number)

        self.logger.info('End of Federation reached. Exiting...')

    def run_simulation(self):
        """
        This function is specifically for the simulation. After the tasks have been performed for a round
        quit, and then the collaborator object will be reinitialized after the next round
        """
        while True:
            tasks = self.get_tasks()
            if  tasks.quit:
                self.logger.info('End of Federation reached. Exiting...')
                break
            elif tasks.sleep_time > 0:
                sleep(tasks.sleep_time) # some sleep function
            else:
                self.logger.info('Received the following tasks: {}'.format(tasks.tasks))
                for task in tasks.tasks:
                    self.do_task(task, tasks.round_number)
                self.logger.info('All tasks completed on {} for round {}...'.format(self.collaborator_name,tasks.round_number))
                break

    def get_tasks(self):

        request  = TasksRequest(header = self.header)
        response = self.client.GetTasks(request)
        self.validate_response(response) # sanity checks and validation

        return response

    def do_task(self, task, round_number):
        # map this task to an actual function name and kwargs
        func_name   = self.task_config[task]['function']
        kwargs      = self.task_config[task]['kwargs']

        # this would return a list of what tensors we require as TensorKeys
        required_tensorkeys_relative = self.task_runner.get_required_tensorkeys_for_function(func_name, **kwargs)

        # models actually return "relative" tensorkeys of (name, LOCAL|GLOBAL, round_offset)
        # so we need to update these keys to their "absolute values"
        required_tensorkeys = []
        for tname, origin, rnd_num, report, tags in required_tensorkeys_relative:
            if origin == 'GLOBAL':
                origin = self.aggregator_uuid
            else:
                origin = self.collaborator_name
            
            #rnd_num is the relative round. So if rnd_num is -1, get the tensor from the previous round
            required_tensorkeys.append(TensorKey(tname, origin, rnd_num + round_number, report, tags))
        
        #print('Required tensorkeys = {}'.format([tk[0] for tk in required_tensorkeys]))
        input_tensor_dict = self.get_numpy_dict_for_tensorkeys(required_tensorkeys)

        # now we have whatever the model needs to do the task
        func = getattr(self.task_runner, func_name)
        global_output_tensor_dict,local_output_tensor_dict = \
                func(col_name=self.collaborator_name,round_num = round_number,input_tensor_dict = input_tensor_dict, **kwargs)

        # Save global and local output_tensor_dicts to TensorDB
        self.tensor_db.cache_tensor(global_output_tensor_dict)
        self.tensor_db.cache_tensor(local_output_tensor_dict)

        # send the results for this tasks; delta and compression will occur in this function
        self.send_task_results(global_output_tensor_dict, round_number, task)

    def get_numpy_dict_for_tensorkeys(self, tensor_keys):
        return {k.tensor_name: self.get_data_for_tensorkey(k) for k in tensor_keys}

    def get_data_for_tensorkey(self, tensor_key):
        """
        This function resolves the tensor corresponding to the requested tensorkey

        Args
        ----
        tensor_key:         Tensorkey that will be resolved locally or remotely. May be the product of other tensors
        extract_metadata:   The requested tensor may have metadata needed for decompression
        """
        # try to get from the store
        tensor_name,origin,round_number,report,tags = tensor_key
        self.logger.debug('Attempting to retrieve tensor {} from local store'.format(tensor_key))
        nparray = self.tensor_db.get_tensor_from_cache(tensor_key)

        # if None and origin is our client, request it from the client
        if nparray is None:
            if origin == self.collaborator_name:
                self.logger.info('Attempting to find locally stored {} tensor from prior round...'.format(tensor_name))
                prior_round = round_number - 1
                while prior_round >= 0:
                    nparray = self.tensor_db.get_tensor_from_cache(TensorKey(tensor_name,origin,prior_round,report,tags))
                    if nparray is not None:
                        self.logger.debug('Found tensor {} in local TensorDB for round {}'.format(tensor_name, prior_round))
                        return nparray
                    prior_round -= 1
                self.logger.info('Cannot find any prior version of tensor {} locally...'.format(tensor_name))
            self.logger.debug('Unable to get tensor from local store...attempting to retrieve from client')
            #Determine whether there are additional compression related dependencies. 
            #Typically, dependencies are only relevant to model layers
            tensor_dependencies = self.tensor_codec.find_dependencies(tensor_key,self.delta_updates)
            #self.logger.info('tensor_dependencies = {}'.format(tensor_dependencies))
            if len(tensor_dependencies) > 0:
                #Resolve dependencies
                #tensor_dependencies[0] corresponds to the prior version of the model. 
                #If it exists locally, should pull the remote delta because this is the least costly path
                prior_model_layer = self.tensor_db.get_tensor_from_cache(tensor_dependencies[0])
                if prior_model_layer is not None:
                    uncompressed_delta = self.get_aggregated_tensor_from_aggregator(tensor_dependencies[1])
                    new_model_tk, nparray = self.tensor_codec.apply_delta(tensor_dependencies[1],uncompressed_delta,prior_model_layer)
                    self.logger.debug('Applied delta to tensor {}'.format(tensor_dependencies[0][0]))
                else:
                    #The original model tensor should be fetched from client
                    nparray = self.get_aggregated_tensor_from_aggregator(tensor_key)
            elif 'model' in tags:
                #Pulling the model for the first time or 
                nparray = self.get_aggregated_tensor_from_aggregator(tensor_key,require_lossless=True)
        else:
            self.logger.debug('Found tensor {} in local TensorDB'.format(tensor_key))

        return nparray

    def get_aggregated_tensor_from_aggregator(self, tensor_key,require_lossless = False):
        """
        This function returns the decompressed tensor associated with the requested tensor key. 
        If the key requests a compressed tensor (in the tag), the tensor will be decompressed before returning
        If the key specifies an uncompressed tensor (or just omits a compressed tag), the decompression operation will be skipped

        Args
        ----
        tensor_key  :               The requested tensor
        permit_lossy_compression:   Should compression of the tensor be allowed in flight? For the initial model, it may
                                    affect convergence to apply lossy compression. And metrics shouldn't be compressed either

        Returns
        -------
        nparray     : The decompressed tensor associated with the requested tensor key
        """
        tensor_name,origin,round_number,report,tags = tensor_key
        request = TensorRequest(header=self.header,
                               tensor_name = tensor_name,
                               round_number = round_number,
                               tags = tags,
                               report = report,
                               require_lossless = require_lossless)

        self.logger.debug('Requesting aggregated tensor {}'.format(tensor_key))
        
        response = self.client.GetAggregatedTensor(request)

      # also do other validation, like on the round_number
        self.validate_response(response)

      # this translates to a numpy array and includes decompression, as necessary
        nparray = self.named_tensor_to_nparray(response.tensor)
        
      # cache this tensor
        self.tensor_db.cache_tensor({tensor_key: nparray})
      # self.logger.info('Printing updated TensorDB: {}'.format(self.tensor_db))

        return nparray
    
    def send_task_results(self, tensor_dict, round_number, task_name):

        named_tensors = [self.nparray_to_named_tensor(k, v) for k, v in tensor_dict.items()]

      # for general tasks, there may be no notion of data size to send. But that raises the question how to properly aggregate results.

        data_size = -1

        if 'train' in task_name:
            data_size = self.task_runner.get_train_data_size()

        if 'valid' in task_name:
            data_size = self.task_runner.get_valid_data_size()

        self.logger.debug(f'{task_name} data size = {data_size}')

        for tensor in tensor_dict:
            tensor_name,origin,fl_round,report,tags = tensor

            if  report:
                self.logger.info(f'Sending metric for task {task_name}, round number {round_number}: {tensor_name}\t{tensor_dict[tensor]}')

        request  = TaskResults(header       = self.header,
                               round_number = round_number,
                               task_name    = task_name,
                               data_size    = data_size,
                               tensors      = named_tensors)

        response = self.client.SendLocalTaskResults(request)

        self.validate_response(response)

    def nparray_to_named_tensor(self,tensor_key, nparray):
        """
        This function constructs the NamedTensor Protobuf and also includes logic to create delta, 
        compress tensors with the TensorCodec, etc.
        """

        # if we have an aggregated tensor, we can make a delta
        tensor_name,origin,round_number,report,tags = tensor_key
        if('trained' in tags and self.delta_updates):
          #Should get the pretrained model to create the delta. If training has happened,
          #Model should already be stored in the TensorDB
          model_nparray = self.tensor_db.get_tensor_from_cache(TensorKey(tensor_name,\
                                                                  origin,\
                                                                  round_number,\
                                                                  report,\
                                                                  ('model',))) 
        
          #The original model will not be present for the optimizer on the first round.
          if model_nparray is not None:
            delta_tensor_key, delta_nparray = self.tensor_codec.generate_delta(tensor_key,nparray,model_nparray)
            delta_comp_tensor_key,delta_comp_nparray,metadata = self.tensor_codec.compress(delta_tensor_key,delta_nparray)
            named_tensor = construct_named_tensor(delta_comp_tensor_key,delta_comp_nparray,metadata,lossless=False)
            return named_tensor

        #Assume every other tensor requires lossless compression
        compressed_tensor_key, compressed_nparray, metadata = \
            self.tensor_codec.compress(tensor_key,nparray,require_lossless=True)
        named_tensor = construct_named_tensor(compressed_tensor_key,compressed_nparray,metadata,lossless=True)
        
        return named_tensor

    def named_tensor_to_nparray(self, named_tensor):
        # do the stuff we do now for decompression and frombuffer and stuff
        # This should probably be moved back to protoutils
        raw_bytes = named_tensor.data_bytes
        metadata = [{'int_to_float': proto.int_to_float,
                     'int_list': proto.int_list,
                     'bool_list': proto.bool_list} for proto in named_tensor.transformer_metadata]
        #The tensor has already been transfered to collaborator, so the newly constructed tensor should have the collaborator origin
        tensor_key = TensorKey(named_tensor.name, self.collaborator_name, named_tensor.round_number, named_tensor.report, tuple(named_tensor.tags))
        tensor_name,origin,round_number,report,tags = tensor_key
        if 'compressed' in tags:
            decompressed_tensor_key, decompressed_nparray =  \
                    self.tensor_codec.decompress(tensor_key,data=raw_bytes,transformer_metadata=metadata,require_lossless=True)
        elif 'lossy_compressed' in tags:
            decompressed_tensor_key, decompressed_nparray =  \
                    self.tensor_codec.decompress(tensor_key,data=raw_bytes,transformer_metadata=metadata)
        else:
            #There could be a case where the compression pipeline is bypassed entirely
            self.logger.warning('Bypassing tensor codec...') 
            decompressed_tensor_key = tensor_key
            decompressed_nparray = raw_bytes

        self.tensor_db.cache_tensor({decompressed_tensor_key: decompressed_nparray})
        
        return decompressed_nparray
