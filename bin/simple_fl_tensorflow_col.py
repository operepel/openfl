#!/usr/bin/env python3
import argparse
import numpy as np

from setup_logging import setup_logging

import tfedlrn
import tfedlrn.collaborator
from tfedlrn.collaborator.collaborator import Collaborator
from tfedlrn.zmqconnection import ZMQClient

from tfedlrn.collaborator.tensorflowmodels.tensorflow2dunet import TensorFlow2DUNet

from tfedlrn.datasets import load_dataset

from tfedlrn.proto.message_pb2 import *

import tensorflow as tf


def main(col_num=0, num_collaborators=4, model_id='TensorFlow2DUNet', device='cuda', server_addr='127.0.0.1', server_port=5555, opt_treatment='RESET'):
    setup_logging()
    agg_id = "simple agg"
    fed_id = "simple fed"
    col_id = "simple col {}".format(col_num)

    connection = ZMQClient('{} connection'.format(col_id), server_addr=server_addr, server_port=server_port)

    # load our data
    if model_id == 'TensorFlow2DUNet':
        X_train, y_train, X_val, y_val = load_dataset('BraTS17_institution',
                                                      institution=col_num,
                                                      channels_first=False)
    else:
        raise NotImplementedError('No model_id {}'.format(model_id))

    model = globals()[model_id](X_train, y_train, X_val, y_val)

    col = Collaborator(col_id, agg_id, fed_id, model, connection, -1, opt_treatment=opt_treatment)

    col.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--col_num', '-c', type=int, default=0)
    parser.add_argument('--num_collaborators', '-n', type=int, default=4)
    parser.add_argument('--model_id', '-m', type=str, choices=['TensorFlow2DUNet'], required=True)
    parser.add_argument('--server_addr', '-sa', type=str, default='127.0.0.1')
    parser.add_argument('--server_port', '-sp', type=int, default=5555)
    parser.add_argument('--opt_treatment', '-ot', type=str, default='RESET')
    args = parser.parse_args()
    main(**vars(args))
