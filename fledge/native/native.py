#This file defines fledge entrypoints to be used directly through python (not CLI)
import os
from copy import copy
from logging import getLogger
import json
from flatten_json import flatten_preserve_lists
import fledge.interface.workspace as workspace
import fledge.interface.aggregator as aggregator
import fledge.interface.collaborator as collaborator
import fledge.interface.plan as plan
from fledge.interface.cli_helper import *

from fledge.component import Aggregator
from fledge.transport import AggregatorGRPCServer
from fledge.component import Collaborator
from fledge.transport import CollaboratorGRPCClient
from fledge.federated import Plan

from fledge.protocols import dump_proto, construct_model_proto
from fledge.utilities import split_tensor_dict_for_holdouts

logger = getLogger(__name__)

WORKSPACE_PREFIX = os.path.join(os.path.expanduser('~'), '.local', 'workspace')

def setup_plan(save=True):
    """
    Dumps the plan with all defaults + overrides set. Returns the plan configuration
    """
    plan_config = 'plan/plan.yaml'
    cols_config = 'plan/cols.yaml'
    data_config = 'plan/data.yaml'
    plan = Plan.Parse(plan_config_path = Path(plan_config),
                      cols_config_path = Path(cols_config),
                      data_config_path = Path(data_config))
    if save:
        Plan.Dump(Path(plan_config), plan.config)

    return plan


def get_plan(return_complete=False):
    """
    Return the flattened JSON associated with the plan
    """

    getLogger().setLevel('CRITICAL')

    plan_config = setup_plan().config

    getLogger().setLevel('INFO')

    flattened_config = flatten_preserve_lists(plan_config,'.')[0]
    if not return_complete:
        keys_to_remove = [k for k,v in flattened_config.items() if ('defaults' in k or v is None)]
    else:
        keys_to_remove = [k for k,v in flattened_config.items() if v is None]
    for k in keys_to_remove:
        del flattened_config[k]

    return flattened_config

def update_plan(config):
    """
    Update the plan with the provided config
    """
    plan_path = 'plan/plan.yaml'
    flat_plan_config = get_plan(return_complete=True)
    for k,v in config.items():
        if k in flat_plan_config:
            flat_plan_config[k] = v
            logger.info(f'Updating {k} to {v}... ')
        else:
            logger.info(f'Key {k} not found in plan. Ignoring... ')
    plan_config = unflatten(flat_plan_config,'.')
    Plan.Dump(Path(plan_path),plan_config)

def unflatten(config,separator='.'):
    while True:
        keys_to_separate = [k for k in config if separator in k]
        if len(keys_to_separate) > 0:
          for key in keys_to_separate:
              prefix = separator.join(key.split(separator)[:-1])
              suffix = key.split(separator)[-1]
              if prefix in config:
                  #print(f'key = {key}')
                  #print(f'config[{prefix}] = {config[prefix]}')
                  temp = {**config[prefix],suffix:config[key]}
                  config[prefix] = temp
              else:
                  config[prefix] = {suffix:config[key]}
              del config[key]
        else:
            return config

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

def init(workspace_template='default', agg_fqdn=None, col_names=['one', 'two']):
    workspace.create(WORKSPACE_PREFIX, workspace_template)
    os.chdir(WORKSPACE_PREFIX)
    workspace.certify()
    aggregator.generate_cert_request(agg_fqdn)
    aggregator.certify(agg_fqdn, silent=True)
    data_path = 1
    for col_name in col_names:
        collaborator.generate_cert_request(col_name, str(data_path), silent=True, skip_package=True)
        collaborator.certify(col_name, silent=True)
        data_path += 1

    setup_logging()


def create_collaborator(plan, name, model, aggregator):

    #Using the same plan object to create multiple collaborators leads to identical collaborator objects.
    #This function can be removed once collaborator generation is fixed in fledge/federated/plan/plan.py
    plan = copy(plan)

    return plan.get_collaborator(name,task_runner=model,client=aggregator)

def run_experiment(collaborator_dict,override_config={}):

    from sys       import path

    file = Path(__file__).resolve()
    root = file.parent.resolve() # interface root, containing command modules
    work = Path.cwd().resolve()

    path.append(   str(root))
    path.insert(0, str(work))

    #Update the plan if necessary
    if len(override_config) > 0:
        update_plan(override_config)

    #TODO: Fix this implementation. The full plan parsing is reused here, 
    #but the model and data will be overwritten based on user specifications
    plan_config = 'plan/plan.yaml'
    cols_config = 'plan/cols.yaml'
    data_config = 'plan/data.yaml'

    plan = Plan.Parse(plan_config_path = Path(plan_config),
                      cols_config_path = Path(cols_config),
                      data_config_path = Path(data_config))


    #Overwrite plan values
    plan.authorized_cols = list(collaborator_dict)
    tensor_pipe = plan.get_tensor_pipe() 

    #This must be set to the final index of the list (this is the last tensorflow session to get created)
    plan.runner_ = list(collaborator_dict.values())[-1]
    model = plan.runner_

    #Initialize model weights
    init_state_path = plan.config['aggregator' ]['settings']['init_state_path']
    rounds_to_train = plan.config['aggregator' ]['settings']['rounds_to_train']
    tensor_dict, holdout_params = split_tensor_dict_for_holdouts(logger, 
                                                                 plan.runner_.get_tensor_dict(False))
    
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
