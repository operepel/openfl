# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import numpy      as np
import tensorflow as tf

from tqdm import tqdm

from fledge.utilities import TensorKey, split_tensor_dict_for_holdouts

from .loader import DataLoader

class FastEstimatorDataLoader(DataLoader):
    """
    Federation Data Loader for FastEstimator
    """

    def __init__(self, batch_size, **kwargs):
        """
        Instantiate the data object

        Args:
            batch_size: Size of batches used for all data loaders
            kwargs: consumes all un-used kwargs

        Returns:
            None
        """

        self.batch_size = batch_size
        self.X_train = None
        self.y_train = None
        self.X_valid = None
        self.y_valid = None

        # Child classes should have init signature:
        # (self, batch_size, **kwargs), should call this __init__ and then
        # define self.X_train, self.y_train, self.X_valid, and self.y_valid


    def get_train_data_size(self):
        """
        Get total number of training samples

        Returns:
            int: number of training samples
        """
        return len(self.pipeline.data['train'])

    def get_valid_data_size(self):
        """
        Get total number of validation samples

        Returns:
            int: number of validation samples
        """
        return len(self.pipeline.data['test'])

    def get_feature_shape(self):
        return self.pipeline.data['train']['x'].shape[1:]


