#!/usr/bin/env python3

# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import argparse
import sys
import os
import logging
import importlib

from tfedlrn.collaborator.collaborator import Collaborator
from tfedlrn.comms.grpc.collaboratorgrpcclient import CollaboratorGRPCClient
from tfedlrn import parse_fl_plan, get_object, load_yaml
from tfedlrn.tensor_transformation_pipelines import get_compression_pipeline

from setup_logging import setup_logging

def get_data(data_names_to_paths, data_name, module_name, class_name, **kwargs):
    """Get the data object for the collaborator

    Args:
        data_names_to_paths: Translate the dataset name to the actual file path for the dataset
        data_name: The dataset name
        module_name: The Python module name
        class_name: The Python class
        **kwargs: Variable arguments to pass to function

    Returns:
        Data object

    """

    # FIXME: I think this method exists in another Python file. Probably could refactor it to single place.
    data_path = data_names_to_paths[data_name]
    return get_object(module_name, class_name, data_path=data_path, **kwargs)

def get_channel(base_dir, cert_common_name, **col_grpc_client_config):
    """Gets the gRPC channel for the collaborator client

    Args:
        base_dir:  The base directory for this collaborator's certificates
        cert_common_name: The certificate name
        **col_grpc_client_config: Additional gRPC config parameters

    Returns:
        A gRPC client object for this collaborator

    """

    cert_dir = os.path.join(base_dir, col_grpc_client_config.pop('cert_folder', 'pki')) # default to 'pki

    return CollaboratorGRPCClient(ca=os.path.join(cert_dir, 'cert_chain.crt'),
                                  certificate=os.path.join(cert_dir, 'col_{}'.format(cert_common_name), 'col_{}.crt'.format(cert_common_name)),
                                  private_key=os.path.join(cert_dir, 'col_{}'.format(cert_common_name), 'col_{}.key'.format(cert_common_name)),
                                  **col_grpc_client_config)

def main(plan, collaborator_common_name, single_col_cert_common_name, data_config_fname, logging_config_fname, logging_default_level):
    """Runs the collaborator client process from the federation (FL) plan

    Args:
        plan: The filename for the federation (FL) plan YAML file
        collaborator_common_name: The common name for the collaborator node
        single_col_cert_common_name: The SSL certificate for this collaborator
        data_config_fname: The dataset configuration filename (YAML)
        logging_config_fname: The log file
        logging_default_level: The log level

    """

    setup_logging(path=logging_config_fname, default_level=logging_default_level)

    # FIXME: consistent filesystem (#15)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(script_dir, 'federations')
    plan_dir = os.path.join(base_dir, 'plans')

    flplan = parse_fl_plan(os.path.join(plan_dir, plan))
    col_config = flplan['collaborator']
    model_config = flplan['model']
    data_config = flplan['data']
    data_names_to_paths = load_yaml(os.path.join(base_dir, data_config_fname))['collaborators']
    if collaborator_common_name not in data_names_to_paths:
        sys.exit("Could not find collaborator id \"{}\" in the local data config file. Please edit \"{}\" to specify the datapaths for this collaborator.".format(collaborator_common_name, data_config_fname))
    data_names_to_paths = data_names_to_paths[collaborator_common_name]
    if data_config['data_name'] not in data_names_to_paths:
        sys.exit("Could not find data path for collaborator id \"{}\" and dataset name \"{}\". Please edit \"{}\" to specify the path (or shard) for this collaborator and dataset.".format(collaborator_common_name, data_config['data_name'], data_config_fname))

    if flplan.get('compression_pipeline') is not None:
        compression_pipeline = get_compression_pipeline(**flplan.get('compression_pipeline'))
    else:
        compression_pipeline = None

    network_config = flplan['network']

    # if a single cert common name is in use, then that is the certificate we must use
    if single_col_cert_common_name is None:
        cert_common_name = collaborator_common_name
    else:
        cert_common_name = single_col_cert_common_name

    channel = get_channel(base_dir=base_dir,
                          cert_common_name=cert_common_name,
                          **network_config)

    data = get_data(data_names_to_paths, **data_config)

    wrapped_model = get_object(data=data, **model_config)

    collaborator = Collaborator(collaborator_common_name=collaborator_common_name,
                                wrapped_model=wrapped_model,
                                channel=channel,
                                compression_pipeline = compression_pipeline,
                                single_col_cert_common_name=single_col_cert_common_name,
                                **col_config)


    collaborator.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', '-p', type=str, required=True)
    parser.add_argument('--collaborator_common_name', '-col', type=str, required=True)
    parser.add_argument('--single_col_cert_common_name', '-scn', type=str, default=None)
    parser.add_argument('--data_config_fname', '-dc', type=str, default="local_data_config.yaml")
    parser.add_argument('--logging_config_fname', '-lc', type=str, default="logging.yaml")
    parser.add_argument('--logging_default_level', '-l', type=str, default="info")
    args = parser.parse_args()
    main(**vars(args))
