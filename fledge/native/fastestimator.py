from pathlib import Path
from logging import getLogger
from fledge.federated import Plan
from fledge.protocols import dump_proto, construct_model_proto
from fledge.utilities import split_tensor_dict_for_holdouts
import fledge.native as fx
from fledge.federated.data import FastEstimatorDataLoader
from fledge.federated.task import FastEstimatorTaskRunner

logger = getLogger(__name__)

class FederatedFastEstimator:
    def __init__(self, estimator, rounds=10, **kwargs):
        self.estimator = estimator
        self.rounds = rounds
        fx.init(**kwargs)

    def fit(self):
        import fastestimator as fe
        from sys       import path

        file = Path(__file__).resolve()
        root = file.parent.resolve() # interface root, containing command modules
        work = Path.cwd().resolve()

        path.append(   str(root))
        path.insert(0, str(work))

        #TODO: Fix this implementation. The full plan parsing is reused here, 
        #but the model and data will be overwritten based on user specifications
        plan_config = (Path(fx.WORKSPACE_PREFIX) / 'plan'/'plan.yaml')
        cols_config = (Path(fx.WORKSPACE_PREFIX) / 'plan'/'cols.yaml')
        data_config = (Path(fx.WORKSPACE_PREFIX) / 'plan'/'data.yaml')

        plan = Plan.Parse(plan_config_path = plan_config,
                        cols_config_path = cols_config,
                        data_config_path = data_config)

        plan.config['aggregator']['settings']['rounds_to_train'] = self.rounds
        plan.rounds_to_train = self.rounds
        self.rounds = plan.config['aggregator' ]['settings']['rounds_to_train']
        data_loader = FastEstimatorDataLoader(self.estimator.pipeline)
        runner = FastEstimatorTaskRunner(self.estimator, data_loader=data_loader)
        #Overwrite plan values
        tensor_pipe = plan.get_tensor_pipe() 
        #Initialize model weights
        init_state_path = plan.config['aggregator' ]['settings']['init_state_path']
        tensor_dict, holdout_params = split_tensor_dict_for_holdouts(logger, 
                                                                    runner.get_tensor_dict(False),
                                                                    {})

        model_snap = construct_model_proto(tensor_dict  = tensor_dict,
                                        round_number = 0,
                                        tensor_pipe  = tensor_pipe)

        logger.info(f'Creating Initial Weights File    🠆 {init_state_path}' )

        dump_proto(model_proto = model_snap, fpath = init_state_path)

        logger.info('Starting Experiment...')
        
        aggregator = plan.get_aggregator()

        model_states = {collaborator: None for collaborator in plan.authorized_cols}
        runners = {}
        data_path = 1
        for col in plan.authorized_cols:
            data = self.estimator.pipeline.data
            train_data, eval_data, test_data = split_data(data['train'], data['eval'], data['test'], data_path, len(plan.authorized_cols))
            pipeline_kwargs = {}
            for k, v in self.estimator.pipeline.__dict__.items():
                if k in ['batch_size', 'ops', 'num_process', 'drop_last', 'pad_value', 'collate_fn']:
                    pipeline_kwargs[k] = v
            pipeline_kwargs.update({'train_data': train_data, 'eval_data': eval_data, 'test_data': test_data})
            pipeline = fe.Pipeline(**pipeline_kwargs)

            data_loader = FastEstimatorDataLoader(pipeline)
            estimator_kwargs = {}
            for k, v in self.estimator.system.__dict__.items():
                if k in ['network', 'traces', 'log_steps', 'max_train_steps_per_epoch', 'max_eval_steps_per_epoch']:
                    estimator_kwargs[k] = v
            estimator_kwargs.update({'pipeline': pipeline, 'epochs': self.estimator.system.total_epochs, 'monitor_names': self.estimator.monitor_names})
            estimator = fe.Estimator(**estimator_kwargs)
            
            runners[col] = FastEstimatorTaskRunner(estimator=estimator, data_loader=data_loader)
            runners[col].set_optimizer_treatment('RESET')
            data_path += 1

        #Create the collaborators
        collaborators = {collaborator: fx.create_collaborator(plan,collaborator,runners[col],aggregator) for collaborator in plan.authorized_cols}

        model = None
        for round_num in range(self.rounds):
            for col in plan.authorized_cols:

                collaborator = collaborators[col]

                if round_num != 0:
                    runners[col].rebuild_model(round_num,model_states[col])

                collaborator.run_simulation()

                model_states[col] = runners[col].get_tensor_dict(with_opt_vars=True)
                model = runners[col].model

        #TODO This will return the model from the last collaborator, NOT the final aggregated model (though they should be similar). 
        #There should be a method added to the aggregator that will load the best model from disk and return it 
        return model

        
def split_data(train,eva,test,rank,collaborator_count):
        """
        Split data into N parts, where N is the collaborator count
        """

        if collaborator_count == 1:
            return train,eva,test

        fraction = [ 1.0 / float(collaborator_count) ] 
        fraction *= (collaborator_count - 1)
        
        #Expand the split list into individual parameters
        train_split = train.split(*fraction)
        eva_split   = eva.split(*fraction)
        test_split  = test.split(*fraction)

        train = [train]
        eva = [eva]
        test = [test]

        if type(train_split) is not list:
            train.append(train_split)
            eva.append(eva_split)
            test.append(test_split)
        else:
            #Combine all partitions into a single list
            train = [train] + train_split
            eva   = [eva] + eva_split
            test  = [test] + test_split

        #Extract the right shard
        train = train[rank-1]
        eva   = eva[rank-1]
        test  = test[rank-1]

        return train,eva,test