import numpy as np
import gzip

from tfedlrn.tensor_transformation_pipelines import TransformationPipeline, Transformer

'''
dictionary:
    'int_to_float': {int:float...}
    'int_list': [128,32,32,3]
    'bool_array': [True, Flase, ...]
---
forward:
        shape
        x = flatten(x)
    sparse(x): topk, metadata = {'int_list': [123...], 'bool_array': np.array(indices )}
    quant(topk): int_array, metadata={'int_float':, int2float_map}
    gzip:(int_array): compressed_bytes; 

backward:
    gzip(compressed_bytes): int_array(flattened)
    quant(int_array, metadata): float_array
    sparse(float_array, metadata): x_original_sparse

'''

class SparsityTransformer(Transformer):
    
    def __init__(self, p=0.01):
        self.p = p
        return

    def forward(self, data, **kwargs):
        """
        Implement the data transformation.
        returns: transformed_data, metadata

        here data is an array value from a model tensor_dict
        """
        '''
        w: model weights, numpy array
        p: sparsity ratio
        '''
        # sparsification
        flatten_data = data.flatten()
        n_elements = flatten_data.shape[0]
        k_op = int(np.ceil(n_elements*self.p))
        topk, topk_indices = self._topk_func(flatten_data, k_op)
        #
        sparse_data = np.zeros(flatten_data.shape)
        sparse_data[topk_indices] = topk 
        nonzero_element_bool_indices = sparse_data != 0.0
        metadata = {}
        metadata['int_list'] = list(data.shape)
        metadata['bool_list'] = nonzero_element_bool_indices
        #print('metadata::', metadata['bool_list'])
        #metadata['topk'] = [topk]
        # metadata['topk_indices'] = [topk_dices]
        # make a sparse data
        return sparse_data, metadata
        '''
        # input::np_array, {}
        # output::np_array, {}
        '''

    def backward(self, data, metadata, **kwargs):
        """
        Implement the data transformation needed when going the oppposite
        direction to the forward method.
        returns: transformed_data
        """
        data_shape = metadata['int_list'] = list(data.shape)
        print('=================================')
        print(metadata.keys())
        print('=================================')
        nonzero_element_bool_indices = metadata['bool_list'] 
        recovered_data = np.zeros(data_shape)
        recovered_data[nonzero_element_bool_indices] = data
        return recovered_data
        
        '''
        shape = data.shape
        # this is an awkward use of the metadata into to float dict, usually it will
        # trully be treated as a dict. Here (and in 'forward' above) we use it essentially as an array.
        shift = np.reshape(np.array([metadata[idx] for idx in range(len(metadata))]), 
                                    newshape=shape, 
                                    order='C')
        return data - shift 
        '''

    def _topk_func(self, x, k):
        # quick sort as default on magnitude
        idx = np.argsort(np.abs(x))
        # sorted order, the right most is the largest magnitude
        length = x.shape[0]
        start_idx = length - k
        # get the top k magnitude
        topk_mag = np.asarray(x[idx[start_idx:]])
        indices = np.asarray(idx[start_idx:])
        return topk_mag, indices

class TernaryTransformer(Transformer):
    def __init__(self, n_cluster):
        self.n_cluster = n_cluster
        return

    def forward(self, data, **kwargs):
        '''
        '''
        # ternarization, data is sparse and flattened
        mean_topk = np.mean(np.abs(data))
        out_ = np.where(data > 0.0, mean_topk, 0.0)
        out = np.where(data < 0.0, -mean_topk, out_)
        int_array, int2float_map = self._float_to_int(out)
        metadata = {}
        metadata['int_to_float']  = int2float_map
        return int_array, metadata

        #results = self.ternary_quant(data, topk)
        #return

    def backward(self, data, metadata, **kwargs):
        # convert back to float
        # TODO
        import copy
        data = copy.deepcopy(data)
        int2float_map = metadata['int_to_float']
        for key in int2float_map:
            indices = data == key
            data[indices] = int2float_map[key]
        return data

    def _float_to_int(self, np_array):
        flatten_array = np_array.reshape(-1)
        unique_value_array = np.unique(flatten_array)
        int_array = np.zeros(flatten_array.shape, dtype=np.int)
        int_to_float_map = {}
        float_to_int_map = {}
        # create table
        for idx, u_value in enumerate(unique_value_array):
            int_to_float_map.update({idx: u_value})
            float_to_int_map.update({u_value: idx})
            # assign to the integer array
            indices = np.where(flatten_array==u_value)
            int_array[indices] = idx
        int_array = int_array.reshape(np_array.shape)
        return int_array, int_to_float_map
            
    def _int_to_float(self, np_array, int_to_float_map):
        flatten_array = np_array.reshape(-1)
        unique_value_array = np.unique(flatten_array)
        float_array = np.zeros(flatten_array.shape, dtype=np.int)
        # create table
        for idx, int_value in enumerate(unique_value_array):
            float_value = int_to_float_map(int_value)
            indices = np.where(np_array==int_value)
            float_array[indices] = float_value
        float_array = float_array.reshape(np_array.shape)
        return int_array, int_to_float_map

class GZIPTransformer(Transformer):
    '''
    How to reshape the integer value np_array?
    np_array -> bytes
    using object compression?
    input::
    output::
    '''
    def __init__(self):
        return

    def forward(self, data, **kwargs):
        bytes_ = data.tobytes()
        compressed_bytes_ = gzip.compress(bytes_)
        #shape_info = data.shape
        metadata = {}
        return compressed_bytes_, metadata

    def backward(self, data, metadata, **kwargs):
        decompressed_bytes_ = gzip.decompress(data)
        data = np.frombuffer(decompressed_bytes_, dtype=np.float32)
        #data = data.reshape(metadata['shape'])
        return data

class STCPipeline(TransformationPipeline):
    
    def __init__(self, p_sparsity=0.01, n_clusters=6, **kwargs):
        # instantiate each transformer
        self.p = p_sparsity
        self.n_cluster = n_clusters
        transformers = [SparsityTransformer(self.p), TernaryTransformer(self.n_cluster), GZIPTransformer()]
        super(STCPipeline, self).__init__(transformers=transformers, **kwargs)
