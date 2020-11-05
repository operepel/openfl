# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import numpy    as np
import torch    as pt
import torch.nn as nn

from copy import deepcopy

from fledge.utilities import TensorKey, split_tensor_dict_for_holdouts

from .runner import TaskRunner

class PyTorchTaskRunner(nn.Module, TaskRunner):
    """PyTorch Model class for Federated Learning
    """

    def __init__(self, device=pt.device('cuda' if pt.cuda.is_available() else 'cpu'), **kwargs):
        """Initializer

        Args:
            device (string): Compute device (default="cpu")
            **kwargs: Additional parameters to pass to the functions
        """

        super().__init__()
        TaskRunner.__init__(self, **kwargs)

        self.device = device
        #This is a map of all the required tensors for each of the public functions in PyTorchTaskRunner
        self.required_tensorkeys_for_function = {}

        self.optimizer = None
        self.loss_fn = None
        self.training_round_completed = False

        # overwrite attribute to account for one optimizer param (in every child model that
        # does not overwrite get and set tensordict) that is not a numpy array
        self.tensor_dict_split_fn_kwargs.update({
                                            'holdout_tensor_names': ['__opt_state_needed']
                                           })

    def rebuild_model(self, round_num, input_tensor_dict,validation = False):
        """
        Parse tensor names and update weights of model. Handles the optimizer treatment

        Returns:
            None
        """
        if self.opt_treatment == 'RESET':
            self.reset_opt_vars()
            self.set_tensor_dict(input_tensor_dict,with_opt_vars=False)
        elif self.training_round_completed and self.opt_treatment == 'CONTINUE_GLOBAL' and not validation:
            self.set_tensor_dict(input_tensor_dict,with_opt_vars=True)
        else:
            self.set_tensor_dict(input_tensor_dict,with_opt_vars=False)

    # models should implement something like this--
    # def train_batches(self, num_batches,use_tqdm = False):
    #     # set to "training" mode
    #     self.train()

    #     losses = []

    #     gen = self.data.get_train_loader()
    #     if use_tqdm:
    #         gen = tqdm.tqdm(gen, desc="training for this round")

    #     batch_num = 0

    #     while batch_num < num_batches:
    #         # shuffling happens every time gen is used as an iterator
    #         for (data, target) in gen:
    #             if batch_num >= num_batches:
    #                 break
    #             else:
    #                 if isinstance(data, np.ndarray):
    #                         data = pt.Tensor(data)
    #                 if isinstance(target, np.ndarray):
    #                     target = pt.Tensor(data)
    #                 data, target = data.to(self.device), target.to(self.device)
    #                 self.optimizer.zero_grad()
    #                 output = self(data)
    #                 loss = self.loss_fn(output, target)
    #                 loss.backward()
    #                 self.optimizer.step()
    #                 losses.append(loss.detach().cpu().numpy())

    #                 batch_num += 1

    #     return np.mean(losses)



    # FIXME: create a good general version. For now, models should implement this
    # def validate(self):
    #     batch_generator = self.data.get_batch_generator(train_or_val='val')
    #     self.eval()
    #     val_score = 0
    #     total_samples = 0

    #     with pt.no_grad():
    #         for data, target in batch_generator:
    #             if isinstance(data, np.ndarray):
    #                 data = pt.Tensor(data)
    #             if isinstance(target, np.ndarray):
    #                 target = pt.Tensor(data)
    #             samples = target.shape[0]
    #             total_samples += samples
    #             data, target = data.to(self.device), target.to(self.device,dtype = pt.int64)
    #             output = self(data)
    #             val_score += self.loss_fn(output, target).cpu().numpy() * samples
    #     return val_score / total_samples

    def get_tensor_dict(self,with_opt_vars = False):
        """Return the tensor dictionary

        Args:
            with_opt_vars (bool): Return the tensor dictionary including the optimizer tensors (Default=False)

        Returns:
            dict: Tensor dictionary {**dict, **optimizer_dict}

        """

        # Gets information regarding tensor model layers and optimizer state.
        # FIXME: self.parameters() instead? Unclear if load_state_dict() or simple assignment is better
        # for now, state dict gives us names which is good
        # FIXME: do both and sanity check each time?

        state = to_cpu_numpy(self.state_dict())

        if with_opt_vars:
            opt_state = _get_optimizer_state(self.optimizer)
            state = {**state, **opt_state}

        return state

    def _get_weights_names(self,with_opt_vars = False):
        # Gets information regarding tensor model layers and optimizer state.
        # FIXME: self.parameters() instead? Unclear if load_state_dict() or simple assignment is better
        # for now, state dict gives us names which is good
        # FIXME: do both and sanity check each time?

        state = self.state_dict().keys()

        if with_opt_vars:
            opt_state = _get_optimizer_state(self.optimizer)
            state += opt_state.keys()

        return state

    def set_tensor_dict(self, tensor_dict,with_opt_vars = False):
        """Set the tensor dictionary

        Args:
            tensor_dict: The tensor dictionary
            with_opt_vars (bool): Return the tensor dictionary including the optimizer tensors (Default=False)

        """
        # Sets tensors for model layers and optimizer state.
        # FIXME: self.parameters() instead? Unclear if load_state_dict() or simple assignment is better
        # for now, state dict gives us names, which is good
        # FIXME: do both and sanity check each time?

        # get device for correct placement of tensors
        device = self.device

        new_state = {}
        # Grabbing keys from model's state_dict helps to confirm we have everything
        for k in self.state_dict():
            new_state[k] = pt.from_numpy(tensor_dict.pop(k)).to(device)

        # set model state
        self.load_state_dict(new_state)

        if with_opt_vars:
            # see if there is state to restore first
            if tensor_dict.pop('__opt_state_needed') == 'true':
                _set_optimizer_state(self.get_optimizer(), device, tensor_dict)

            # sanity check that we did not record any state that was not used
            assert len(tensor_dict) == 0

    def get_optimizer(self):
        return self.optimizer

    def get_required_tensorkeys_for_function(self, func_name, **kwargs):
        """
        Get the required tensors for specified function that could be called as part of a task.
        By default, this is just all of the layers and optimizer of the model.

        Args:
            func_name

        Returns:
            list : [TensorKey]
        """

        if func_name == 'validate':
            local_model = 'apply=' + str(kwargs['apply'])
            return self.required_tensorkeys_for_function[func_name][local_model]
        else:
            return self.required_tensorkeys_for_function[func_name]

    def initialize_tensorkeys_for_functions(self,with_opt_vars=False):
        """Set the required tensors for all publicly accessible methods that could be called as part of a task.
        By default, this is just all of the layers and optimizer of the model. Custom tensors should be added to this function

        Args:
            None

        Returns:
            None
        """

        #TODO there should be a way to programmatically iterate through all of the methods in the class and declare the tensors.
        #For now this is done manually

        output_model_dict = self.get_tensor_dict(with_opt_vars=with_opt_vars)
        global_model_dict,local_model_dict = split_tensor_dict_for_holdouts(self.logger, output_model_dict, **self.tensor_dict_split_fn_kwargs)
        if not with_opt_vars:
            validation_global_model_dict = global_model_dict
            validation_local_model_dict = local_model_dict
        else:
            output_model_dict = self.get_tensor_dict(with_opt_vars=False)
            validation_global_model_dict, validation_local_model_dict = split_tensor_dict_for_holdouts(self.logger, output_model_dict, **self.tensor_dict_split_fn_kwargs)


        self.required_tensorkeys_for_function['train_batches'] = [TensorKey(tensor_name,'GLOBAL',0,False,('model',)) for tensor_name in global_model_dict]
        self.required_tensorkeys_for_function['train_batches'] += [TensorKey(tensor_name,'LOCAL',0,False,('model',)) for tensor_name in local_model_dict]
        
        self.required_tensorkeys_for_function['train'] = [TensorKey(tensor_name,'GLOBAL',0,False,('model',)) for tensor_name in global_model_dict]
        self.required_tensorkeys_for_function['train'] += [TensorKey(tensor_name,'LOCAL',0,False,('model',)) for tensor_name in local_model_dict]

        #Validation may be performed on local or aggregated (global) model, so there is an extra lookup dimension for kwargs
        self.required_tensorkeys_for_function['validate'] = {}
        #TODO This is not stateless. The optimizer will not be
        self.required_tensorkeys_for_function['validate']['apply=local'] = \
                [TensorKey(tensor_name,'LOCAL',0,False,('trained',)) for tensor_name in {**validation_global_model_dict,**validation_local_model_dict}]
        self.required_tensorkeys_for_function['validate']['apply=global'] = \
                [TensorKey(tensor_name,'GLOBAL',0,False,('model',)) for tensor_name in validation_global_model_dict]
        self.required_tensorkeys_for_function['validate']['apply=global'] += \
                [TensorKey(tensor_name,'LOCAL',0,False,('model',)) for tensor_name in validation_local_model_dict]

    def load_native(self, filepath, model_state_dict_key='model_state_dict', optimizer_state_dict_key='optimizer_state_dict', **kwargs):
        """Loads model and optimizer states from a pickled file specified by filepath. model_/optimizer_state_dict args can be specified if needed. Uses pt.load().

        Args:
            filepath (string)                   : Path to pickle file created by pt.save().
            model_state_dict_key (string)       : key for model state dict in pickled file.
            optimizer_state_dict_key (string)   : key for optimizer state dict in picked file.
            kwargs                              : unused

        Returns:
            None
        """
        pickle_dict = pt.load(filepath)
        self.load_state_dict(pickle_dict[model_state_dict_key])
        self.optimizer.load_state_dict(pickle_dict[optimizer_state_dict_key])

    def save_native(self, filepath, model_state_dict_key='model_state_dict', optimizer_state_dict_key='optimizer_state_dict', **kwargs):
        """Saves model and optimizer states in a picked file specified by the filepath. model_/optimizer_state_dicts are stored in the keys provided. Uses pt.save().

        Args:
            filepath (string)                   : Path to pickle file to be created by pt.save().
            model_state_dict_key (string)       : key for model state dict in pickled file.
            optimizer_state_dict_key (string)   : key for optimizer state dict in picked file.
            kwargs                              : unused

        Returns:
            None
        """
        pickle_dict = {model_state_dict_key: self.state_dict(), optimizer_state_dict_key: self.optimizer.state_dict()}
        pt.save(pickle_dict, filepath)

    def reset_opt_vars(self):
        """
        Reset optimizer variables

        Resets the optimizer variables

        """
        pass


def _derive_opt_state_dict(opt_state_dict):
    """Separate optimizer tensors from the tensor dictionary

    Flattens the optimizer state dict so as to have key, value pairs with values as numpy arrays.
    The keys have sufficient info to restore opt_state_dict using expand_derived_opt_state_dict.

    Args:
        opt_state_dict: The optimizer state dictionary

    """

    derived_opt_state_dict = {}

    # Determine if state is needed for this optimizer.
    if len(opt_state_dict['state']) == 0:
        derived_opt_state_dict['__opt_state_needed'] = 'false'
        return derived_opt_state_dict

    derived_opt_state_dict['__opt_state_needed'] = 'true'

    # Using one example state key, we collect keys for the corresponding dictionary value.
    example_state_key = opt_state_dict['param_groups'][0]['params'][0]
    example_state_subkeys = set(opt_state_dict['state'][example_state_key].keys())

    # We assume that the state collected for all params in all param groups is the same.
    # We also assume that whether or not the associated values to these state subkeys
    #   is a tensor depends only on the subkey.
    # Using assert statements to break the routine if these assumptions are incorrect.
    for state_key in opt_state_dict['state'].keys():
        assert example_state_subkeys == set(opt_state_dict['state'][state_key].keys())
        for state_subkey in example_state_subkeys:
            assert isinstance(opt_state_dict['state'][example_state_key][state_subkey], pt.Tensor) == \
                isinstance(opt_state_dict['state'][state_key][state_subkey], pt.Tensor)

    state_subkeys = list(opt_state_dict['state'][example_state_key].keys())

    # Tags will record whether the value associated to the subkey is a tensor or not.
    state_subkey_tags = []
    for state_subkey in state_subkeys:
        if isinstance(opt_state_dict['state'][example_state_key][state_subkey], pt.Tensor):
            state_subkey_tags.append('istensor')
        else:
            state_subkey_tags.append('')
    state_subkeys_and_tags = list(zip(state_subkeys, state_subkey_tags))

    # Forming the flattened dict, using a concatenation of group index, subindex, tag,
    # and subkey inserted into the flattened dict key - needed for reconstruction.
    nb_params_per_group = []
    for group_idx, group in enumerate(opt_state_dict['param_groups']):
        for idx, param_id in enumerate(group['params']):
            for subkey, tag in state_subkeys_and_tags:
                if tag == 'istensor':
                    new_v = opt_state_dict['state'][param_id][subkey].cpu().numpy()
                else:
                    new_v = np.array([opt_state_dict['state'][param_id][subkey]])
                derived_opt_state_dict['__opt_state_{}_{}_{}_{}'.format(group_idx, idx, tag, subkey)] = new_v
        nb_params_per_group.append(idx + 1)
    # group lengths are also helpful for reconstructing original opt_state_dict structure
    derived_opt_state_dict['__opt_group_lengths'] = np.array(nb_params_per_group)

    return derived_opt_state_dict

def expand_derived_opt_state_dict(derived_opt_state_dict, device):
    """Expand the optimizer state dictionary

    Takes a derived opt_state_dict and creates an opt_state_dict suitable as
    input for load_state_dict for restoring optimizer state.

    Reconstructing state_subkeys_and_tags using the example key
    prefix, "__opt_state_0_0_", certain to be present.

    Args:
        derived_opt_state_dict: Optimizer state dictionary

    Returns:
        dict: Optimizer state dictionary
    """
    state_subkeys_and_tags = []
    for key in derived_opt_state_dict:
        if key.startswith('__opt_state_0_0_'):
            stripped_key = key[16:]
            if stripped_key.startswith('istensor_'):
                this_tag = 'istensor'
                subkey = stripped_key[9:]
            else:
                this_tag = ''
                subkey = stripped_key[1:]
            state_subkeys_and_tags.append((subkey, this_tag))

    opt_state_dict = {'param_groups': [], 'state': {}}
    nb_params_per_group = list(derived_opt_state_dict.pop('__opt_group_lengths').astype(np.int))

    # Construct the expanded dict.
    for group_idx, nb_params in enumerate(nb_params_per_group):
        these_group_ids = ['{}_{}'.format(group_idx, idx) for idx in range(nb_params)]
        opt_state_dict['param_groups'].append({'params': these_group_ids})
        for this_id in these_group_ids:
            opt_state_dict['state'][this_id] = {}
            for subkey, tag in state_subkeys_and_tags:
                flat_key = '__opt_state_{}_{}_{}'.format(this_id, tag, subkey)
                if tag == 'istensor':
                    new_v = pt.from_numpy(derived_opt_state_dict.pop(flat_key))
                else:
                    # Here (for currrently supported optimizers) the subkey should be 'step'
                    # and the length of array should be one.
                    assert subkey == 'step'
                    assert len(derived_opt_state_dict[flat_key]) == 1
                    new_v = int(derived_opt_state_dict.pop(flat_key))
                opt_state_dict['state'][this_id][subkey] = new_v


    # sanity check that we did not miss any optimizer state
    assert len(derived_opt_state_dict) == 0

    return opt_state_dict

def _get_optimizer_state(optimizer):
    """Return the optimizer state

    Args:
        optimizer
    """

    opt_state_dict = deepcopy(optimizer.state_dict())
    derived_opt_state_dict = _derive_opt_state_dict(opt_state_dict)

    return derived_opt_state_dict

def _set_optimizer_state(optimizer, device, derived_opt_state_dict):
    """Sets the optimizer state

    Args:
        optimizer:
        device:
        derived_opt_state_dict:

    """

    temp_state_dict = expand_derived_opt_state_dict(derived_opt_state_dict, device)

    # FIXME: Figure out whether or not this breaks learning rate scheduling and the like.
    # Setting default values.
    # All optimizer.defaults are considered as not changing over course of training.
    for group in temp_state_dict['param_groups']:
        for k, v in optimizer.defaults.items():
            group[k] = v

    optimizer.load_state_dict(temp_state_dict)

def to_cpu_numpy(state):
    """Send data to CPU as Numpy array

    Args:
        state

    """
    # deep copy so as to decouple from active model
    state = deepcopy(state)

    for k, v in state.items():
        # When restoring, we currently assume all values are tensors.
        if not pt.is_tensor(v):
            raise ValueError('We do not currently support non-tensors '
                                      'coming from model.state_dict()')
        state[k] = v.cpu().numpy()  # get as a numpy array, making sure is on cpu
    return state
