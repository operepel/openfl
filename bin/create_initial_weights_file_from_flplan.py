#!/usr/bin/env python3

# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import argparse
import os
import logging
import importlib

from tfedlrn.tensor_transformation_pipelines import get_compression_pipeline, NoCompressionPipeline
from tfedlrn import load_yaml, get_object, split_tensor_dict_for_holdouts, parse_fl_plan
from tfedlrn.proto.protoutils import dump_proto, construct_proto
from setup_logging import setup_logging

def get_data(data_names_to_paths, data_name, module_name, class_name, **kwargs):
    """Creates a data object from the data path

    Args:
        data_names_to_paths: Dictionary to convert data_name to file path
        data_name: Name of the dataset to use from the data configuration file
        module_name: Class module for the model
        class_name: Model class name
        **kwargs: Additional variable arguments to pass to the function

    Returns:
        A data object

    """
    data_path = data_names_to_paths[data_name]
    return get_object(module_name, class_name, data_path=data_path, **kwargs)

def main(plan, collaborators_file, feature_shape, data_config_fname, logging_config_path, logging_default_level):
    """Creates a protobuf file of the initial weights for the model

    Uses the federation (FL) plan to create an initial weights file
    for the federation.

    Args:
        plan: The federation (FL) plan filename
        collaborators_file:
        feature_shape: The input shape to the model
        data_config_fname: The data configuration file (defines where the datasets are located)
        logging_config_path: The log path
        logging_default_level (int): The default log level

    """

    setup_logging(path=logging_config_path, default_level=logging_default_level)

    logger = logging.getLogger(__name__)

    # FIXME: consistent filesystem (#15)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(script_dir, 'federations')

    plan_dir = os.path.join(base_dir, 'plans')
    weights_dir = os.path.join(base_dir, 'weights')
    if not os.path.exists(weights_dir):
        print('creating folder:', weights_dir)
        os.makedirs(weights_dir)

    plan = parse_fl_plan(os.path.join(plan_dir, plan))
    model_config = plan['model']
    agg_config = plan['aggregator']
    data_config = plan['data']

    # For now we are compressing initial models if a compression pipeline exists
    if plan.get('compression_pipeline') is not None:
        compression_pipeline = get_compression_pipeline(**plan.get('compression_pipeline'))
    else:
        compression_pipeline = NoCompressionPipeline()


    if feature_shape is None:
        if collaborators_file is None:
            sys.exit("You must specify either a feature shape or a collaborator list in order for the script to determine the input layer shape")
        # FIXME: this will ultimately run in a governor environment and should not require any data to work
        # pick the first collaborator to create the data and model (could be any)
        collaborator_common_name = load_yaml(os.path.join(base_dir, 'collaborator_lists', collaborators_file))['collaborator_common_names'][0]
        data_names_to_paths = load_yaml(os.path.join(base_dir, data_config_fname))['collaborators'][collaborator_common_name]
        data = get_data(data_names_to_paths, **data_config)
    else:
        data = get_object('data.dummy', 'RandomData', feature_shape=feature_shape)
        logger.info('Using data object of type {} and feature shape {}'.format(type(data), feature_shape))

    wrapped_model = get_object(data=data, **model_config)

    fpath = os.path.join(weights_dir, agg_config['init_model_fname'])

    tensor_dict_split_fn_kwargs = wrapped_model.tensor_dict_split_fn_kwargs or {}

    tensor_dict, holdout_params = split_tensor_dict_for_holdouts(logger,
                                                                 wrapped_model.get_tensor_dict(False),
                                                                 **tensor_dict_split_fn_kwargs)
    logger.warn('Following paramters omitted from global initial model, '\
                'local initialization will determine values: {}'.format(list(holdout_params.keys())))

    model_proto = construct_proto(tensor_dict=tensor_dict,
                                  model_id=wrapped_model.__class__.__name__,
                                  model_version=0,
                                  is_delta=False,
                                  delta_from_version=-1,
                                  compression_pipeline=compression_pipeline)

    dump_proto(model_proto=model_proto, fpath=fpath)

    logger.info("Created initial weights file: {}".format(fpath))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', '-p', type=str, required=True)
    parser.add_argument('--collaborators_file', '-c', type=str, default=None, help="Name of YAML File in /bin/federations/collaborator_lists/")
    parser.add_argument('--feature_shape', '-fs', type=int, nargs='+', default=None)
    parser.add_argument('--data_config_fname', '-dc', type=str, default="local_data_config.yaml")
    parser.add_argument('--logging_config_path', '-lcp', type=str, default="logging.yaml")
    parser.add_argument('--logging_default_level', '-l', type=str, default="info")
    args = parser.parse_args()
    main(**vars(args))
