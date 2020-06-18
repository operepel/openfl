# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: collaborator_aggregator_interface.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='collaborator_aggregator_interface.proto',
  package='tfedlrn_proto',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\'collaborator_aggregator_interface.proto\x12\rtfedlrn_proto\"+\n\nDataStream\x12\x0c\n\x04size\x18\x01 \x01(\r\x12\x0f\n\x07npbytes\x18\x02 \x01(\x0c\"\xab\x01\n\rMetadataProto\x12\x42\n\x0cint_to_float\x18\x01 \x03(\x0b\x32,.tfedlrn_proto.MetadataProto.IntToFloatEntry\x12\x10\n\x08int_list\x18\x02 \x03(\x05\x12\x11\n\tbool_list\x18\x03 \x03(\x08\x1a\x31\n\x0fIntToFloatEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x02:\x02\x38\x01\"k\n\x0bTensorProto\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\ndata_bytes\x18\x03 \x01(\x0c\x12:\n\x14transformer_metadata\x18\x04 \x03(\x0b\x32\x1c.tfedlrn_proto.MetadataProto\"Z\n\rMessageHeader\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x11\n\trecipient\x18\x02 \x01(\t\x12\x15\n\rfederation_id\x18\x03 \x01(\t\x12\x0f\n\x07\x63ounter\x18\x04 \x01(\x05\"*\n\x0bModelHeader\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\x05\"e\n\nModelProto\x12*\n\x06header\x18\x01 \x01(\x0b\x32\x1a.tfedlrn_proto.ModelHeader\x12+\n\x07tensors\x18\x02 \x03(\x0b\x32\x1a.tfedlrn_proto.TensorProto\"\x8b\x01\n\x10LocalModelUpdate\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12(\n\x05model\x18\x02 \x01(\x0b\x32\x19.tfedlrn_proto.ModelProto\x12\x11\n\tdata_size\x18\x03 \x01(\x05\x12\x0c\n\x04loss\x18\x04 \x01(\x02\"\x9c\x01\n\x16LocalValidationResults\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12\x30\n\x0cmodel_header\x18\x02 \x01(\x0b\x32\x1a.tfedlrn_proto.ModelHeader\x12\x0f\n\x07results\x18\x03 \x01(\x02\x12\x11\n\tdata_size\x18\x04 \x01(\x05\"l\n\nJobRequest\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12\x30\n\x0cmodel_header\x18\x02 \x01(\x0b\x32\x1a.tfedlrn_proto.ModelHeader\"v\n\x14ModelDownloadRequest\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12\x30\n\x0cmodel_header\x18\x02 \x01(\x0b\x32\x1a.tfedlrn_proto.ModelHeader\"\xd2\x01\n\x0eRoundTaskQuery\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12V\n\x16task_results_last_sync\x18\x02 \x03(\x0b\x32\x36.tfedlrn_proto.RoundTaskQuery.TaskResultsLastSyncEntry\x1a:\n\x18TaskResultsLastSyncEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x05:\x02\x38\x01\"k\n\x11GlobalModelUpdate\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12(\n\x05model\x18\x02 \x01(\x0b\x32\x19.tfedlrn_proto.ModelProto\"Y\n\x08JobReply\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12\x1f\n\x03job\x18\x02 \x01(\x0e\x32\x12.tfedlrn_proto.Job\"C\n\x13LocalModelUpdateAck\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\"I\n\x19LocalValidationResultsAck\x12,\n\x06header\x18\x01 \x01(\x0b\x32\x1c.tfedlrn_proto.MessageHeader*[\n\x03Job\x12\r\n\tJOB_TRAIN\x10\x00\x12\x10\n\x0cJOB_VALIDATE\x10\x01\x12\r\n\tJOB_YIELD\x10\x02\x12\x0c\n\x08JOB_QUIT\x10\x03\x12\x16\n\x12JOB_DOWNLOAD_MODEL\x10\x04\x32\xf1\x02\n\nAggregator\x12\x42\n\nRequestJob\x12\x19.tfedlrn_proto.JobRequest\x1a\x17.tfedlrn_proto.JobReply\"\x00\x12S\n\rDownloadModel\x12#.tfedlrn_proto.ModelDownloadRequest\x1a\x19.tfedlrn_proto.DataStream\"\x00\x30\x01\x12[\n\x16UploadLocalModelUpdate\x12\x19.tfedlrn_proto.DataStream\x1a\".tfedlrn_proto.LocalModelUpdateAck\"\x00(\x01\x12m\n\x18UploadLocalMetricsUpdate\x12%.tfedlrn_proto.LocalValidationResults\x1a(.tfedlrn_proto.LocalValidationResultsAck\"\x00\x62\x06proto3')
)

_JOB = _descriptor.EnumDescriptor(
  name='Job',
  full_name='tfedlrn_proto.Job',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='JOB_TRAIN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='JOB_VALIDATE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='JOB_YIELD', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='JOB_QUIT', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='JOB_DOWNLOAD_MODEL', index=4, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1713,
  serialized_end=1804,
)
_sym_db.RegisterEnumDescriptor(_JOB)

Job = enum_type_wrapper.EnumTypeWrapper(_JOB)
JOB_TRAIN = 0
JOB_VALIDATE = 1
JOB_YIELD = 2
JOB_QUIT = 3
JOB_DOWNLOAD_MODEL = 4



_DATASTREAM = _descriptor.Descriptor(
  name='DataStream',
  full_name='tfedlrn_proto.DataStream',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='size', full_name='tfedlrn_proto.DataStream.size', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='npbytes', full_name='tfedlrn_proto.DataStream.npbytes', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=58,
  serialized_end=101,
)


_METADATAPROTO_INTTOFLOATENTRY = _descriptor.Descriptor(
  name='IntToFloatEntry',
  full_name='tfedlrn_proto.MetadataProto.IntToFloatEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tfedlrn_proto.MetadataProto.IntToFloatEntry.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tfedlrn_proto.MetadataProto.IntToFloatEntry.value', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=226,
  serialized_end=275,
)

_METADATAPROTO = _descriptor.Descriptor(
  name='MetadataProto',
  full_name='tfedlrn_proto.MetadataProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='int_to_float', full_name='tfedlrn_proto.MetadataProto.int_to_float', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='int_list', full_name='tfedlrn_proto.MetadataProto.int_list', index=1,
      number=2, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='bool_list', full_name='tfedlrn_proto.MetadataProto.bool_list', index=2,
      number=3, type=8, cpp_type=7, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_METADATAPROTO_INTTOFLOATENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=104,
  serialized_end=275,
)


_TENSORPROTO = _descriptor.Descriptor(
  name='TensorProto',
  full_name='tfedlrn_proto.TensorProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='tfedlrn_proto.TensorProto.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data_bytes', full_name='tfedlrn_proto.TensorProto.data_bytes', index=1,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='transformer_metadata', full_name='tfedlrn_proto.TensorProto.transformer_metadata', index=2,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=277,
  serialized_end=384,
)


_MESSAGEHEADER = _descriptor.Descriptor(
  name='MessageHeader',
  full_name='tfedlrn_proto.MessageHeader',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sender', full_name='tfedlrn_proto.MessageHeader.sender', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='recipient', full_name='tfedlrn_proto.MessageHeader.recipient', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='federation_id', full_name='tfedlrn_proto.MessageHeader.federation_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='counter', full_name='tfedlrn_proto.MessageHeader.counter', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=386,
  serialized_end=476,
)


_MODELHEADER = _descriptor.Descriptor(
  name='ModelHeader',
  full_name='tfedlrn_proto.ModelHeader',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='tfedlrn_proto.ModelHeader.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='tfedlrn_proto.ModelHeader.version', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=478,
  serialized_end=520,
)


_MODELPROTO = _descriptor.Descriptor(
  name='ModelProto',
  full_name='tfedlrn_proto.ModelProto',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.ModelProto.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='tensors', full_name='tfedlrn_proto.ModelProto.tensors', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=522,
  serialized_end=623,
)


_LOCALMODELUPDATE = _descriptor.Descriptor(
  name='LocalModelUpdate',
  full_name='tfedlrn_proto.LocalModelUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.LocalModelUpdate.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model', full_name='tfedlrn_proto.LocalModelUpdate.model', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data_size', full_name='tfedlrn_proto.LocalModelUpdate.data_size', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='loss', full_name='tfedlrn_proto.LocalModelUpdate.loss', index=3,
      number=4, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=626,
  serialized_end=765,
)


_LOCALVALIDATIONRESULTS = _descriptor.Descriptor(
  name='LocalValidationResults',
  full_name='tfedlrn_proto.LocalValidationResults',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.LocalValidationResults.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model_header', full_name='tfedlrn_proto.LocalValidationResults.model_header', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='results', full_name='tfedlrn_proto.LocalValidationResults.results', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data_size', full_name='tfedlrn_proto.LocalValidationResults.data_size', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=768,
  serialized_end=924,
)


_JOBREQUEST = _descriptor.Descriptor(
  name='JobRequest',
  full_name='tfedlrn_proto.JobRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.JobRequest.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model_header', full_name='tfedlrn_proto.JobRequest.model_header', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=926,
  serialized_end=1034,
)


_MODELDOWNLOADREQUEST = _descriptor.Descriptor(
  name='ModelDownloadRequest',
  full_name='tfedlrn_proto.ModelDownloadRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.ModelDownloadRequest.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model_header', full_name='tfedlrn_proto.ModelDownloadRequest.model_header', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1036,
  serialized_end=1154,
)


_ROUNDTASKQUERY_TASKRESULTSLASTSYNCENTRY = _descriptor.Descriptor(
  name='TaskResultsLastSyncEntry',
  full_name='tfedlrn_proto.RoundTaskQuery.TaskResultsLastSyncEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tfedlrn_proto.RoundTaskQuery.TaskResultsLastSyncEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tfedlrn_proto.RoundTaskQuery.TaskResultsLastSyncEntry.value', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1309,
  serialized_end=1367,
)

_ROUNDTASKQUERY = _descriptor.Descriptor(
  name='RoundTaskQuery',
  full_name='tfedlrn_proto.RoundTaskQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.RoundTaskQuery.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='task_results_last_sync', full_name='tfedlrn_proto.RoundTaskQuery.task_results_last_sync', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_ROUNDTASKQUERY_TASKRESULTSLASTSYNCENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1157,
  serialized_end=1367,
)


_GLOBALMODELUPDATE = _descriptor.Descriptor(
  name='GlobalModelUpdate',
  full_name='tfedlrn_proto.GlobalModelUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.GlobalModelUpdate.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model', full_name='tfedlrn_proto.GlobalModelUpdate.model', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1369,
  serialized_end=1476,
)


_JOBREPLY = _descriptor.Descriptor(
  name='JobReply',
  full_name='tfedlrn_proto.JobReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.JobReply.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='job', full_name='tfedlrn_proto.JobReply.job', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1478,
  serialized_end=1567,
)


_LOCALMODELUPDATEACK = _descriptor.Descriptor(
  name='LocalModelUpdateAck',
  full_name='tfedlrn_proto.LocalModelUpdateAck',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.LocalModelUpdateAck.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1569,
  serialized_end=1636,
)


_LOCALVALIDATIONRESULTSACK = _descriptor.Descriptor(
  name='LocalValidationResultsAck',
  full_name='tfedlrn_proto.LocalValidationResultsAck',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='tfedlrn_proto.LocalValidationResultsAck.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1638,
  serialized_end=1711,
)

_METADATAPROTO_INTTOFLOATENTRY.containing_type = _METADATAPROTO
_METADATAPROTO.fields_by_name['int_to_float'].message_type = _METADATAPROTO_INTTOFLOATENTRY
_TENSORPROTO.fields_by_name['transformer_metadata'].message_type = _METADATAPROTO
_MODELPROTO.fields_by_name['header'].message_type = _MODELHEADER
_MODELPROTO.fields_by_name['tensors'].message_type = _TENSORPROTO
_LOCALMODELUPDATE.fields_by_name['header'].message_type = _MESSAGEHEADER
_LOCALMODELUPDATE.fields_by_name['model'].message_type = _MODELPROTO
_LOCALVALIDATIONRESULTS.fields_by_name['header'].message_type = _MESSAGEHEADER
_LOCALVALIDATIONRESULTS.fields_by_name['model_header'].message_type = _MODELHEADER
_JOBREQUEST.fields_by_name['header'].message_type = _MESSAGEHEADER
_JOBREQUEST.fields_by_name['model_header'].message_type = _MODELHEADER
_MODELDOWNLOADREQUEST.fields_by_name['header'].message_type = _MESSAGEHEADER
_MODELDOWNLOADREQUEST.fields_by_name['model_header'].message_type = _MODELHEADER
_ROUNDTASKQUERY_TASKRESULTSLASTSYNCENTRY.containing_type = _ROUNDTASKQUERY
_ROUNDTASKQUERY.fields_by_name['header'].message_type = _MESSAGEHEADER
_ROUNDTASKQUERY.fields_by_name['task_results_last_sync'].message_type = _ROUNDTASKQUERY_TASKRESULTSLASTSYNCENTRY
_GLOBALMODELUPDATE.fields_by_name['header'].message_type = _MESSAGEHEADER
_GLOBALMODELUPDATE.fields_by_name['model'].message_type = _MODELPROTO
_JOBREPLY.fields_by_name['header'].message_type = _MESSAGEHEADER
_JOBREPLY.fields_by_name['job'].enum_type = _JOB
_LOCALMODELUPDATEACK.fields_by_name['header'].message_type = _MESSAGEHEADER
_LOCALVALIDATIONRESULTSACK.fields_by_name['header'].message_type = _MESSAGEHEADER
DESCRIPTOR.message_types_by_name['DataStream'] = _DATASTREAM
DESCRIPTOR.message_types_by_name['MetadataProto'] = _METADATAPROTO
DESCRIPTOR.message_types_by_name['TensorProto'] = _TENSORPROTO
DESCRIPTOR.message_types_by_name['MessageHeader'] = _MESSAGEHEADER
DESCRIPTOR.message_types_by_name['ModelHeader'] = _MODELHEADER
DESCRIPTOR.message_types_by_name['ModelProto'] = _MODELPROTO
DESCRIPTOR.message_types_by_name['LocalModelUpdate'] = _LOCALMODELUPDATE
DESCRIPTOR.message_types_by_name['LocalValidationResults'] = _LOCALVALIDATIONRESULTS
DESCRIPTOR.message_types_by_name['JobRequest'] = _JOBREQUEST
DESCRIPTOR.message_types_by_name['ModelDownloadRequest'] = _MODELDOWNLOADREQUEST
DESCRIPTOR.message_types_by_name['RoundTaskQuery'] = _ROUNDTASKQUERY
DESCRIPTOR.message_types_by_name['GlobalModelUpdate'] = _GLOBALMODELUPDATE
DESCRIPTOR.message_types_by_name['JobReply'] = _JOBREPLY
DESCRIPTOR.message_types_by_name['LocalModelUpdateAck'] = _LOCALMODELUPDATEACK
DESCRIPTOR.message_types_by_name['LocalValidationResultsAck'] = _LOCALVALIDATIONRESULTSACK
DESCRIPTOR.enum_types_by_name['Job'] = _JOB
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DataStream = _reflection.GeneratedProtocolMessageType('DataStream', (_message.Message,), dict(
  DESCRIPTOR = _DATASTREAM,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.DataStream)
  ))
_sym_db.RegisterMessage(DataStream)

MetadataProto = _reflection.GeneratedProtocolMessageType('MetadataProto', (_message.Message,), dict(

  IntToFloatEntry = _reflection.GeneratedProtocolMessageType('IntToFloatEntry', (_message.Message,), dict(
    DESCRIPTOR = _METADATAPROTO_INTTOFLOATENTRY,
    __module__ = 'collaborator_aggregator_interface_pb2'
    # @@protoc_insertion_point(class_scope:tfedlrn_proto.MetadataProto.IntToFloatEntry)
    ))
  ,
  DESCRIPTOR = _METADATAPROTO,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.MetadataProto)
  ))
_sym_db.RegisterMessage(MetadataProto)
_sym_db.RegisterMessage(MetadataProto.IntToFloatEntry)

TensorProto = _reflection.GeneratedProtocolMessageType('TensorProto', (_message.Message,), dict(
  DESCRIPTOR = _TENSORPROTO,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.TensorProto)
  ))
_sym_db.RegisterMessage(TensorProto)

MessageHeader = _reflection.GeneratedProtocolMessageType('MessageHeader', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEHEADER,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.MessageHeader)
  ))
_sym_db.RegisterMessage(MessageHeader)

ModelHeader = _reflection.GeneratedProtocolMessageType('ModelHeader', (_message.Message,), dict(
  DESCRIPTOR = _MODELHEADER,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.ModelHeader)
  ))
_sym_db.RegisterMessage(ModelHeader)

ModelProto = _reflection.GeneratedProtocolMessageType('ModelProto', (_message.Message,), dict(
  DESCRIPTOR = _MODELPROTO,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.ModelProto)
  ))
_sym_db.RegisterMessage(ModelProto)

LocalModelUpdate = _reflection.GeneratedProtocolMessageType('LocalModelUpdate', (_message.Message,), dict(
  DESCRIPTOR = _LOCALMODELUPDATE,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.LocalModelUpdate)
  ))
_sym_db.RegisterMessage(LocalModelUpdate)

LocalValidationResults = _reflection.GeneratedProtocolMessageType('LocalValidationResults', (_message.Message,), dict(
  DESCRIPTOR = _LOCALVALIDATIONRESULTS,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.LocalValidationResults)
  ))
_sym_db.RegisterMessage(LocalValidationResults)

JobRequest = _reflection.GeneratedProtocolMessageType('JobRequest', (_message.Message,), dict(
  DESCRIPTOR = _JOBREQUEST,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.JobRequest)
  ))
_sym_db.RegisterMessage(JobRequest)

ModelDownloadRequest = _reflection.GeneratedProtocolMessageType('ModelDownloadRequest', (_message.Message,), dict(
  DESCRIPTOR = _MODELDOWNLOADREQUEST,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.ModelDownloadRequest)
  ))
_sym_db.RegisterMessage(ModelDownloadRequest)

RoundTaskQuery = _reflection.GeneratedProtocolMessageType('RoundTaskQuery', (_message.Message,), dict(

  TaskResultsLastSyncEntry = _reflection.GeneratedProtocolMessageType('TaskResultsLastSyncEntry', (_message.Message,), dict(
    DESCRIPTOR = _ROUNDTASKQUERY_TASKRESULTSLASTSYNCENTRY,
    __module__ = 'collaborator_aggregator_interface_pb2'
    # @@protoc_insertion_point(class_scope:tfedlrn_proto.RoundTaskQuery.TaskResultsLastSyncEntry)
    ))
  ,
  DESCRIPTOR = _ROUNDTASKQUERY,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.RoundTaskQuery)
  ))
_sym_db.RegisterMessage(RoundTaskQuery)
_sym_db.RegisterMessage(RoundTaskQuery.TaskResultsLastSyncEntry)

GlobalModelUpdate = _reflection.GeneratedProtocolMessageType('GlobalModelUpdate', (_message.Message,), dict(
  DESCRIPTOR = _GLOBALMODELUPDATE,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.GlobalModelUpdate)
  ))
_sym_db.RegisterMessage(GlobalModelUpdate)

JobReply = _reflection.GeneratedProtocolMessageType('JobReply', (_message.Message,), dict(
  DESCRIPTOR = _JOBREPLY,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.JobReply)
  ))
_sym_db.RegisterMessage(JobReply)

LocalModelUpdateAck = _reflection.GeneratedProtocolMessageType('LocalModelUpdateAck', (_message.Message,), dict(
  DESCRIPTOR = _LOCALMODELUPDATEACK,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.LocalModelUpdateAck)
  ))
_sym_db.RegisterMessage(LocalModelUpdateAck)

LocalValidationResultsAck = _reflection.GeneratedProtocolMessageType('LocalValidationResultsAck', (_message.Message,), dict(
  DESCRIPTOR = _LOCALVALIDATIONRESULTSACK,
  __module__ = 'collaborator_aggregator_interface_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.LocalValidationResultsAck)
  ))
_sym_db.RegisterMessage(LocalValidationResultsAck)


_METADATAPROTO_INTTOFLOATENTRY._options = None
_ROUNDTASKQUERY_TASKRESULTSLASTSYNCENTRY._options = None

_AGGREGATOR = _descriptor.ServiceDescriptor(
  name='Aggregator',
  full_name='tfedlrn_proto.Aggregator',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=1807,
  serialized_end=2176,
  methods=[
  _descriptor.MethodDescriptor(
    name='RequestJob',
    full_name='tfedlrn_proto.Aggregator.RequestJob',
    index=0,
    containing_service=None,
    input_type=_JOBREQUEST,
    output_type=_JOBREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DownloadModel',
    full_name='tfedlrn_proto.Aggregator.DownloadModel',
    index=1,
    containing_service=None,
    input_type=_MODELDOWNLOADREQUEST,
    output_type=_DATASTREAM,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UploadLocalModelUpdate',
    full_name='tfedlrn_proto.Aggregator.UploadLocalModelUpdate',
    index=2,
    containing_service=None,
    input_type=_DATASTREAM,
    output_type=_LOCALMODELUPDATEACK,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UploadLocalMetricsUpdate',
    full_name='tfedlrn_proto.Aggregator.UploadLocalMetricsUpdate',
    index=3,
    containing_service=None,
    input_type=_LOCALVALIDATIONRESULTS,
    output_type=_LOCALVALIDATIONRESULTSACK,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_AGGREGATOR)

DESCRIPTOR.services_by_name['Aggregator'] = _AGGREGATOR

# @@protoc_insertion_point(module_scope)
