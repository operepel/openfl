#!/usr/bin/env python3

# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import argparse
import os
import logging

from tfedlrn.flplan import parse_fl_plan, load_yaml, create_aggregator_object_from_flplan, create_aggregator_server_from_flplan, get_serve_kwargs_from_flpan
from setup_logging import setup_logging


def main(plan, collaborators_file, single_col_cert_common_name, logging_config_path, logging_default_level):
    setup_logging(path=logging_config_path, default_level=logging_default_level)

    # FIXME: consistent filesystem (#15)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.join(script_dir, 'federations')
    plan_dir = os.path.join(base_dir, 'plans')
    weights_dir = os.path.join(base_dir, 'weights')
    collaborators_dir = os.path.join(base_dir, 'collaborator_lists')

    flplan = parse_fl_plan(os.path.join(plan_dir, plan))
    collaborator_common_names = load_yaml(os.path.join(collaborators_dir, collaborators_file))['collaborator_common_names']

    agg             = create_aggregator_object_from_flplan(flplan, collaborator_common_names, single_col_cert_common_name, weights_dir)
    server          = create_aggregator_server_from_flplan(agg, flplan)
    serve_kwargs    = get_serve_kwargs_from_flpan(flplan, base_dir)
    
    server.serve(**serve_kwargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', '-p', type=str, required=True)
    parser.add_argument('--collaborators_file', '-c', type=str, required=True, help="Name of YAML File in /bin/federations/collaborator_lists/")
    parser.add_argument('--single_col_cert_common_name', '-scn', type=str, default=None)
    parser.add_argument('--logging_config_path', '-lcp', type=str, default="logging.yaml")
    parser.add_argument('--logging_default_level', '-l', type=str, default="info")
    args = parser.parse_args()
    main(**vars(args))
