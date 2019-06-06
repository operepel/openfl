import pickle
import glob
import os
import socket

import numpy as np
from math import ceil


def _get_dataset_func_map():
    return {
        'mnist': load_mnist,
#         'fashion-mnist': load_fashion_mnist,
#         'pubfig83': load_pubfig83,
#         'cifar10': load_cifar10,
#         'cifar20': load_cifar20,
#         'cifar100': load_cifar100,
#         'bsm': load_bsm,
#         'BraTS17': load_BraTS17,
    }


def get_dataset_list():
    return list(_get_dataset_func_map().keys())


def load_dataset(dataset, **kwargs):
    if dataset not in get_dataset_list():
        raise ValueError("Dataset {} not in list of datasets {get_dataset_list()}".format(dataset))
    return _get_dataset_func_map()[dataset](**kwargs)


def _get_dataset_dir(server=None):
    if server is None:
        server = socket.gethostname()
    server_to_path = {'spr-gpu01': os.path.join('/', 'raid', 'datasets'),
                      'edwardsb-Z270X-UD5': os.path.join('/', 'data'),
                      'msheller-ubuntu': os.path.join('/', 'home', 'msheller', 'datasets')}
    return server_to_path[server]


def _unpickle(file):
    with open(file, 'rb') as fo:
        d = pickle.load(fo, encoding='bytes')
    return d


def _read_mnist(path, **kwargs):
    X_train, y_train = _read_mnist_kind(path, kind='train', **kwargs)
    X_test, y_test = _read_mnist_kind(path, kind='t10k', **kwargs)

    return X_train, y_train, X_test, y_test


# from https://github.com/zalandoresearch/fashion-mnist/blob/master/utils/mnist_reader.py
def _read_mnist_kind(path, kind='train', one_hot=True, **kwargs):
    import os
    import gzip
    import numpy as np

    """Load MNIST data from `path`"""
    labels_path = os.path.join(path,
                               '%s-labels-idx1-ubyte.gz'
                               % kind)
    images_path = os.path.join(path,
                               '%s-images-idx3-ubyte.gz'
                               % kind)

    with gzip.open(labels_path, 'rb') as lbpath:
        labels = np.frombuffer(lbpath.read(), dtype=np.uint8,
                               offset=8)

    with gzip.open(images_path, 'rb') as imgpath:
        images = np.frombuffer(imgpath.read(), dtype=np.uint8,
                               offset=16).reshape(len(labels), 784)

    images = images.astype(float) / 255
    if one_hot:
        labels = _one_hot(labels.astype(np.int), 10)

    return images, labels


def load_mnist(**kwargs):
    path = os.path.join(_get_dataset_dir(), 'mnist', 'input_data')
    return _read_mnist(path, **kwargs)


def load_fashion_mnist(**kwargs):
    path = os.path.join(_get_dataset_dir(), 'fashion-mnist')
    return _read_mnist(path, **kwargs)


def _one_hot(y, n):
    return np.eye(n)[y]