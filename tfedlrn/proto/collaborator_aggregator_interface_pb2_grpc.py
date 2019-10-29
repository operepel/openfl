# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import tfedlrn.proto.collaborator_aggregator_interface_pb2 as collaborator__aggregator__interface__pb2


class AggregatorStub(object):
  """we start with everything as "required" while developing / debugging. This forces correctness better.
  FIXME: move to "optional" once development is complete

  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.RequestJob = channel.unary_unary(
        '/tfedlrn_proto.Aggregator/RequestJob',
        request_serializer=collaborator__aggregator__interface__pb2.JobRequest.SerializeToString,
        response_deserializer=collaborator__aggregator__interface__pb2.JobReply.FromString,
        )
    self.DownloadModel = channel.unary_unary(
        '/tfedlrn_proto.Aggregator/DownloadModel',
        request_serializer=collaborator__aggregator__interface__pb2.ModelDownloadRequest.SerializeToString,
        response_deserializer=collaborator__aggregator__interface__pb2.GlobalModelUpdate.FromString,
        )
    self.UploadLocalModelUpdate = channel.unary_unary(
        '/tfedlrn_proto.Aggregator/UploadLocalModelUpdate',
        request_serializer=collaborator__aggregator__interface__pb2.LocalModelUpdate.SerializeToString,
        response_deserializer=collaborator__aggregator__interface__pb2.LocalModelUpdateAck.FromString,
        )
    self.UploadLocalMetricsUpdate = channel.unary_unary(
        '/tfedlrn_proto.Aggregator/UploadLocalMetricsUpdate',
        request_serializer=collaborator__aggregator__interface__pb2.LocalValidationResults.SerializeToString,
        response_deserializer=collaborator__aggregator__interface__pb2.LocalValidationResultsAck.FromString,
        )


class AggregatorServicer(object):
  """we start with everything as "required" while developing / debugging. This forces correctness better.
  FIXME: move to "optional" once development is complete

  """

  def RequestJob(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DownloadModel(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def UploadLocalModelUpdate(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def UploadLocalMetricsUpdate(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_AggregatorServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'RequestJob': grpc.unary_unary_rpc_method_handler(
          servicer.RequestJob,
          request_deserializer=collaborator__aggregator__interface__pb2.JobRequest.FromString,
          response_serializer=collaborator__aggregator__interface__pb2.JobReply.SerializeToString,
      ),
      'DownloadModel': grpc.unary_unary_rpc_method_handler(
          servicer.DownloadModel,
          request_deserializer=collaborator__aggregator__interface__pb2.ModelDownloadRequest.FromString,
          response_serializer=collaborator__aggregator__interface__pb2.GlobalModelUpdate.SerializeToString,
      ),
      'UploadLocalModelUpdate': grpc.unary_unary_rpc_method_handler(
          servicer.UploadLocalModelUpdate,
          request_deserializer=collaborator__aggregator__interface__pb2.LocalModelUpdate.FromString,
          response_serializer=collaborator__aggregator__interface__pb2.LocalModelUpdateAck.SerializeToString,
      ),
      'UploadLocalMetricsUpdate': grpc.unary_unary_rpc_method_handler(
          servicer.UploadLocalMetricsUpdate,
          request_deserializer=collaborator__aggregator__interface__pb2.LocalValidationResults.FromString,
          response_serializer=collaborator__aggregator__interface__pb2.LocalValidationResultsAck.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'tfedlrn_proto.Aggregator', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
