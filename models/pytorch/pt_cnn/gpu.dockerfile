ARG whoami
FROM tfl_agg_pt_cnn_$whoami:0.1

# FIXME: this is only for the MNIST data object and should ultimately be removed!
RUN pip3 install tensorflow-gpu==1.14.0
RUN pip3 install torch==1.2.0