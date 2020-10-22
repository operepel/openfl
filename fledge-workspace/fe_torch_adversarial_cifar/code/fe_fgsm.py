# Copyright (C) 2020 Intel Corporation
# Licensed subject to the terms of the separately executed evaluation license agreement between Intel Corporation and you.

import numpy            as np

from fledge.federated import FastEstimatorTaskRunner
from fledge.utilities import TensorKey

from logging import getLogger

import fastestimator as fe
from fastestimator.architecture.pytorch import LeNet
from fastestimator.backend import to_tensor, argmax
from fastestimator.dataset.data import cifar10
from fastestimator.op.numpyop.meta import Sometimes
from fastestimator.op.numpyop.multivariate import HorizontalFlip
from fastestimator.op.numpyop.univariate import CoarseDropout, Normalize, Onehot
from fastestimator.op.tensorop import Average
from fastestimator.op.tensorop.gradient import Watch, FGSM
from fastestimator.op.tensorop.loss import CrossEntropy
from fastestimator.op.tensorop.model import ModelOp, UpdateOp
from fastestimator.trace.io import BestModelSaver
from fastestimator.trace.metric import Accuracy
from fastestimator.util import ImgData, to_number

logger = getLogger(__name__)

class FastEstimatorFGSM(FastEstimatorTaskRunner):
    """
    An FGSM example based on the LeNet model
    """
    def __init__(self, **kwargs):
        """
        Initializer

        Args:
            **kwargs: Additional parameters to pass to the function
        """
        super().__init__(**kwargs)

        

        #Now the data pipeline will be initialized and the rest of the network/estimator can be built
        self.network = self.build_network()
        self.estimator = self.build_estimator()

        self.set_logger()

        self.initialize_tensorkeys_for_functions()

        logger.info(self.model.__repr__())

        if  self.data_loader is not None:
            logger.info(f'Train Set Size : {self.get_train_data_size()}')
            logger.info(f'Valid Set Size : {self.get_valid_data_size()}')

    def build_model(self):
        """
        Define the FastEstimator model architecture.

        Args:
            None

        Returns:
            model: Union[tf.keras.sequential, nn.module]

        """

        model = fe.build(model_fn=lambda: LeNet(input_shape=(3, 32, 32)), \
                         optimizer_fn="adam", model_name="adv_model")
        return model

    def build_network(self):
        """
        Define the FastEstimator network flow

        Args:
            None

        Returns:
            network: KerasNetwork object
        """

        epsilon = 0.04

        network = fe.Network(ops=[
                Watch(inputs="x"),
                ModelOp(model=self.model, inputs="x", outputs="y_pred"),
                CrossEntropy(inputs=("y_pred", "y"), outputs="base_ce"),
                FGSM(data="x", loss="base_ce", outputs="x_adverse", epsilon=epsilon),
                ModelOp(model=self.model, inputs="x_adverse", outputs="y_pred_adv"),
                CrossEntropy(inputs=("y_pred_adv", "y"), outputs="adv_ce"),
                Average(inputs=("base_ce", "adv_ce"), outputs="avg_ce"),
                UpdateOp(model=self.model, loss_name="avg_ce")
            ])

        return network

    def build_estimator(self):
        """
        Define the estimator to run the experiment (this will persist throughout the lifetime 
        of the TaskRunner) 

        Args:
            None

        Returns:
            estimator: Estimator object
        """

        max_train_steps_per_epoch=None
        max_eval_steps_per_epoch=None

        traces = [
            Accuracy(true_key="y", pred_key="y_pred", output_name="clean_accuracy"),
            Accuracy(true_key="y", pred_key="y_pred_adv", output_name="adversarial_accuracy"),
        ]
        estimator = fe.Estimator(pipeline=self.data_loader.pipeline,
                                 network=self.network,
                                 epochs=2,
                                 traces=traces,
                                 max_train_steps_per_epoch=max_train_steps_per_epoch,
                                 max_eval_steps_per_epoch=max_eval_steps_per_epoch,
                                 monitor_names=["base_ce", "adv_ce"],
                                 log_steps=1000)
        
        return estimator
