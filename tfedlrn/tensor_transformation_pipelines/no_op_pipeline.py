from tfedlrn.tensor_transformation_pipelines import TransformationPipeline


class NoOpPipeline(TransformationPipeline):
    
    def __init__(self, **kwargs):
        super(NoOpPipeline, self).__init__(transformers=[])

    
