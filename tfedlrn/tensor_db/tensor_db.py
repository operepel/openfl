import pandas as pd
import numpy as np
from threading import Lock
from tfedlrn import TensorKey

class TensorDB(object):
    """
    The TensorDB stores a tensor key and the data that it corresponds to. It is built on top of a pandas dataframe
    for it's easy insertion, retreival and aggregation capabilities. Each collaborator and aggregator has its own TensorDB.
    """
    def __init__(self):
        self.tensor_db = pd.DataFrame([], columns=['tensor_name','origin','round','tags','nparray'])
        self.mutex = Lock()

    def __repr__(self):
        with pd.option_context('display.max_rows', None):
            return 'TensorDB contents:\n{}'.format(self.tensor_db[['tensor_name','origin','round','tags']])

    def __str__(self):
        return self.__repr__()


    def cache_tensor(self, tensor_key_dict):
        """
        Insert tensor into TensorDB (dataframe)

	Parameters:
	-----------
        tensor_key_dict:	{tensor_key: nparray}

        Returns
	-------
	None
        """

        self.mutex.acquire(blocking=True)
        try:
            for tensor_key,nparray in tensor_key_dict.items():
                tensor_name,origin,round,tags = tensor_key
                df = pd.DataFrame([[tensor_name,origin,round,tags,nparray]], \
                                  columns=['tensor_name','origin','round','tags','nparray'])
                self.tensor_db = pd.concat([self.tensor_db,df],ignore_index=True)
        finally:
            self.mutex.release()


    def get_tensor_from_cache(self, tensor_key):
        """
        Performs a lookup of the tensor_key in the TensorDB. Returns the nparray if it is available
        Otherwise, it returns 'None'
        """

        tensor_name,origin,round,tags = tensor_key

        #TODO come up with easy way to ignore compression
        df = self.tensor_db[(self.tensor_db['tensor_name'] == tensor_name) & \
                            (self.tensor_db['origin'] == origin) & \
                            (self.tensor_db['round'] == round) & \
                            (self.tensor_db['tags'] == tags)]

        if len(df) == 0:
            return None
        return np.array(df['nparray'].iloc[0])

    def get_aggregated_tensor(self, tensor_key, collaborator_weight_dict):
        """
        Determines whether all of the collaborator tensors are present for a given tensor key, and returns their weighted average 

        Parameters
        ----------
        tensor_key:		        The tensor key to be resolved. If origin 'agg_uuid' is present, 
                                        can be returned directly. Otherwise must compute weighted average of all collaborators
        collaborator_weight_dict:	List of collaborator names in federation and their respective weights

        Returns
        -------
        weighted_nparray if all collaborator values are present
        None if not all values are present
        
        """
        if len(collaborator_weight_dict) != 0:
            assert(sum(collaborator_weight_dict.values()) >= 0.99 and \
                   sum(collaborator_weight_dict.values()) <= 1.01), \
                   "Collaborator weights are not normalized"
        collaborator_names = collaborator_weight_dict.keys()
        agg_tensor_dict = {}
        
        #Check if the aggregated tensor is already present in TensorDB
        tensor_name,origin,round,tags = tensor_key

        raw_df = self.tensor_db[(self.tensor_db['tensor_name'] == tensor_name) & \
                                (self.tensor_db['origin'] == origin) & \
                                (self.tensor_db['round'] == round) & \
                                (self.tensor_db['tags'] == tags)]['nparray']
        if len(raw_df) > 0:
            return np.array(raw_df.iloc[0])

        for col in collaborator_names:
            if(type(tags) == str):
                new_tags = tuple([tags] + [col])
            else:
                new_tags = tuple(list(tags) + [col])
            raw_df = self.tensor_db[(self.tensor_db['tensor_name'] == tensor_name) & \
                                    (self.tensor_db['origin'] == origin) & \
                                    (self.tensor_db['round'] == round) & \
                                    (self.tensor_db['tags'] == new_tags)]['nparray']
            #print(raw_df)
            if len(raw_df) == 0:
                print('No results for collaborator {}, TensorKey={}'.format(\
                        col,TensorKey(tensor_name,origin,round,new_tags)))
                return None
            else:
                agg_tensor_dict[col] = raw_df.iloc[0]
            agg_tensor_dict[col] = agg_tensor_dict[col] * collaborator_weight_dict[col] 
        agg_nparray = np.sum([agg_tensor_dict[col] for col in collaborator_names],axis=0)
        
        #Cache aggregated tensor in TensorDB
        self.cache_tensor({tensor_key: agg_nparray})

        return np.array(agg_nparray)            
