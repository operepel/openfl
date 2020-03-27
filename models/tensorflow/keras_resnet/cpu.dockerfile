# Copyright (C) 2020 Intel Corporation
# Licensed subject to Collaboration Agreement dated February 28th, 2020 between Intel Corporation and Trustees of the University of Pennsylvania.

ARG whoami
FROM tfl_agg_mnist_cnn_keras_$whoami:0.1

# Only use one CPU thread to train the model
#   to avoid the significant communication overhead.
ENV OMP_NUM_THREADS=1
ENV KMP_BLOCKTIME=30
ENV KMP_SETTINGS=1
ENV KMP_AFFINITY=granularity=fine,verbose,compact,1,0

RUN pip3 install intel-tensorflow==1.14.0;