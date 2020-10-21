#This file defines fledge entrypoints to be used directly through python (not CLI)
import os
from copy import copy
from logging import getLogger
from fledge.interface.cli_helper import *
from fledge.component import Aggregator
from fledge.transport import AggregatorGRPCServer
from fledge.component import Collaborator
from fledge.transport import CollaboratorGRPCClient
from fledge.federated import Plan

from fledge.protocols import dump_proto, construct_model_proto
from fledge.utilities import split_tensor_dict_for_holdouts

logger = getLogger(__name__)


def setup_logging():
    #Setup logging
    from logging import basicConfig
    from rich.console   import Console
    from rich.logging   import RichHandler
    import pkgutil
    if (True if pkgutil.find_loader('tensorflow') else False):
        import tensorflow as tf
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR) 
    console = Console(width = 160)
    basicConfig(level = 'INFO', format = '%(message)s', datefmt = '[%X]', handlers = [RichHandler(console = console)])    

def init():
    #TODO Add function to setup a default workspace in ~/.local/workspace
    setup_logging()


def create_collaborator(plan, name, model, aggregator):

    #Using the same plan object to create multiple collaborators leads to identical collaborator objects.
    #This function can be removed once collaborator generation is fixed in fledge/federated/plan/plan.py
    plan = copy(plan)

    return plan.get_collaborator(name,task_runner=model,client=aggregator)

def setup_pki(aggregator_fqdn, collaborator_names):
    """
    Params
    ------
        aggregator_fqdn: str   - aggregator fqdn (this can be resolved with socket.get_fqdn()
        collaborator_names: 
    """
    pass


def patch_plan(config,plan):
    """

    Strawman function (not used yet):

    The config is a dictionary of parameters that should be patched into the default plan

    Ideally, the parameter would be simplified to something like 'round_to_train' instead of the 
    triple nested dict config['aggregator']['settings']['rounds_to_train']

    This is not as trivial as it sounds, because there are special Plan (as in, the plan class) variables
    that need to be overwritten as well. One way simplifying this complexity is patching the plan, 
    saving the new plan, the reloading the plan again
    """

    for param in config:
      reference_to_plan_config = find_plan_param(param,plan)
      reference_to_plan_config[param] = config[param]

    #Save plan
    Dump('plan/plan_modified.yaml',plan)

    #Reinitialize plan
    plan = Plan.Parse(plan_config_path = Path(plan_config),
                      cols_config_path = Path(cols_config),
                      data_config_path = Path(data_config))

    return plan


def run_experiment(collaborator_dict,config={}):

    from sys       import path

    file = Path(__file__).resolve()
    root = file.parent.resolve() # interface root, containing command modules
    work = Path.cwd().resolve()

    path.append(   str(root))
    path.insert(0, str(work))

    #TODO: Fix this implementation. The full plan parsing is reused here, 
    #but the model and data will be overwritten based on user specifications
    plan_config = 'plan/plan.yaml'
    cols_config = 'plan/cols.yaml'
    data_config = 'plan/data.yaml'

    plan = Plan.Parse(plan_config_path = Path(plan_config),
                      cols_config_path = Path(cols_config),
                      data_config_path = Path(data_config))

    if 'rounds_to_train' in config:
        plan.config['aggregator']['settings']['rounds_to_train'] = config['rounds_to_train']
        plan.rounds_to_train = config['rounds_to_train']
    rounds_to_train = plan.config['aggregator' ]['settings']['rounds_to_train'] 

    if 'tasks.locally_tuned_model_validation.aggregation_type' in config:
        plan.config['tasks']['locally_tuned_model_validation']['aggregation_type'] = config['tasks.locally_tuned_model_validation.aggregation_type']
        #logger.info('custom aggregation type set')
        #logger.info(f'{plan.config}')

    #Overwrite plan values
    plan.authorized_cols = list(collaborator_dict)
    tensor_pipe = plan.get_tensor_pipe() 

    #This must be set to the final index of the list (this is the last tensorflow session to get created)
    plan.runner_ = list(collaborator_dict.values())[-1]
    model = plan.runner_

    #Do PKI setup here 

    #setup_pki(aggregator_fqdn,collaborator_names)

    #Set rounds to train


    #Initialize model weights
    init_state_path = plan.config['aggregator' ]['settings']['init_state_path']
    tensor_dict, holdout_params = split_tensor_dict_for_holdouts(logger, 
                                                                 plan.runner_.get_tensor_dict(False),
                                                                 {})

    model_snap = construct_model_proto(tensor_dict  = tensor_dict,
                                       round_number = 0,
                                       tensor_pipe  = tensor_pipe)

    logger.info(f'Creating Initial Weights File    🠆 {init_state_path}' )

    dump_proto(model_proto = model_snap, fpath = init_state_path)

    logger.info('Starting Experiment...')
    
    aggregator = plan.get_aggregator()

    model_states = {collaborator: None for collaborator in collaborator_dict.keys()}

    #Create the collaborators
    collaborators = {collaborator: create_collaborator(plan,collaborator,model,aggregator) for collaborator in plan.authorized_cols}

    for round_num in range(rounds_to_train):
        for col in plan.authorized_cols:

            collaborator = collaborators[col]
            model.set_data_loader(collaborator_dict[col].data_loader)

            if round_num != 0:
                model.rebuild_model(round_num,model_states[col])

            collaborator.run_simulation()

            model_states[col] = model.get_tensor_dict(with_opt_vars=True)

    #TODO This will return the model from the last collaborator, NOT the final aggregated model (though they should be similar). 
    #There should be a method added to the aggregator that will load the best model from disk and return it 
    return model
