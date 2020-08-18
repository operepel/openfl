# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import numpy as np
import torch
import torch.utils.data

from data.fldata import FLData


class PyTorchFLDataInMemory(FLData):
    """PyTorch data loader for Federated Learning
    """

    def __init__(self, batch_size, **kwargs):
        """Instantiate the data object

        Args:
            batch_size (int): batch size for all data loaders
            kwargs: consumes all un-used kwargs

        """
        self.batch_size = batch_size
        self.train_loader = None
        self.val_loader = None
        self.inference_loader = None
        self.training_data_size = None
        self.validation_data_size = None

        # Child classes should have init signature:
        # (self, data_path, batch_size, **kwargs), should call this __init__ and then
        # define loaders: self.train_loader and self.val_loader using the
        # self.create_loader provided here.

    def get_feature_shape(self):
        """Get the shape of an example feature array

        Returns:
            tuple: shape of an example feature array
        """
        return tuple(self.train_loader.dataset[0][0].shape)

    def get_train_loader(self):
        """Get training data loader

        Returns:
            loader object (class defined by inheritor)
        """
        return self.train_loader

    def get_val_loader(self):
        """Get validation data loader

        Returns:
            loader object (class defined by inheritor)
        """
        # TODO: Do we want to be able to modify batch size here?
        # If so will have to decide whether to replace the loader.
        return self.val_loader

    def get_inference_loader(self):
        """
        Get inferencing data loader 

        Returns
        -------
        loader object (class defined by inheritor)
        """
        return self.inference_loader

    def get_training_data_size(self):
        """Get total number of training samples

        Returns:
            int : number of training samples
        """
        return self.training_data_size

    def get_validation_data_size(self):
        """Get total number of validation samples

        Returns:
            int: number of validation samples
        """
        return self.validation_data_size


    def create_loader(self, X, y, shuffle, batch_size=None):
        """Create the data loader using the Torch Tensor methods

        Args:
            X: the input data
            y: the label data
            shuffle: whether to shuffle in-between batch draws

        Returns:
            A `PyTorch DataLoader object <https://pytorch.org/docs/1.1.0/_modules/torch/utils/data/dataloader.html`_
        """
        if batch_size is None:
            batch_size = self.batch_size
        # DEBUG
        print('\nlength of data: ', len(X))
        if isinstance(X[0], np.ndarray):
            tX = torch.stack([torch.Tensor(i) for i in X])
        else:
            tX = torch.Tensor(X)
        if y is None:
            return torch.utils.data.DataLoader(dataset=torch.utils.data.TensorDataset(tX), 
                                               batch_size=self.batch_size, 
                                               shuffle=shuffle)
        else:
            if isinstance(y[0], np.ndarray):
                ty = torch.stack([torch.Tensor(i) for i in y])
            else:
                ty = torch.Tensor(y)
            return torch.utils.data.DataLoader(dataset=torch.utils.data.TensorDataset(tX, ty), 
                                               batch_size=batch_size, 
                                               shuffle=shuffle)




        
