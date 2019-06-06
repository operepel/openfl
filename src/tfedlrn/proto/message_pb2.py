# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/message.proto

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
  name='proto/message.proto',
  package='tfedlrn_proto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x13proto/message.proto\x12\rtfedlrn_proto\"\x90\x04\n\tFLMessage\x12;\n\x10localmodelupdate\x18\x01 \x01(\x0b\x32\x1f.tfedlrn_proto.LocalModelUpdateH\x00\x12G\n\x16localvalidationresults\x18\x02 \x01(\x0b\x32%.tfedlrn_proto.LocalValidationResultsH\x00\x12/\n\njobrequest\x18\x03 \x01(\x0b\x32\x19.tfedlrn_proto.JobRequestH\x00\x12\x43\n\x14modeldownloadrequest\x18\x04 \x01(\x0b\x32#.tfedlrn_proto.ModelDownloadRequestH\x00\x12=\n\x11globalmodelupdate\x18\x05 \x01(\x0b\x32 .tfedlrn_proto.GlobalModelUpdateH\x00\x12+\n\x08jobreply\x18\x06 \x01(\x0b\x32\x17.tfedlrn_proto.JobReplyH\x00\x12\x41\n\x13localmodelupdateack\x18\x07 \x01(\x0b\x32\".tfedlrn_proto.LocalModelUpdateAckH\x00\x12M\n\x19localvalidationresultsack\x18\x08 \x01(\x0b\x32(.tfedlrn_proto.LocalValidationResultsAckH\x00\x42\t\n\x07payload\":\n\x0bTensorProto\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\r\n\x05shape\x18\x02 \x03(\x05\x12\x0e\n\x06values\x18\x03 \x03(\x02\"Z\n\rMessageHeader\x12\x0e\n\x06sender\x18\x01 \x02(\t\x12\x11\n\trecipient\x18\x02 \x02(\t\x12\x15\n\rfederation_id\x18\x03 \x02(\t\x12\x0f\n\x07\x63ounter\x18\x04 \x02(\x05\"*\n\x0bModelHeader\x12\n\n\x02id\x18\x01 \x02(\t\x12\x0f\n\x07version\x18\x02 \x02(\x05\"e\n\nModelProto\x12*\n\x06header\x18\x01 \x02(\x0b\x32\x1a.tfedlrn_proto.ModelHeader\x12+\n\x07tensors\x18\x02 \x03(\x0b\x32\x1a.tfedlrn_proto.TensorProto\"\x8b\x01\n\x10LocalModelUpdate\x12,\n\x06header\x18\x01 \x02(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12(\n\x05model\x18\x02 \x02(\x0b\x32\x19.tfedlrn_proto.ModelProto\x12\x11\n\tdata_size\x18\x03 \x02(\x05\x12\x0c\n\x04loss\x18\x04 \x02(\x02\"\x9c\x01\n\x16LocalValidationResults\x12,\n\x06header\x18\x01 \x02(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12\x30\n\x0cmodel_header\x18\x02 \x02(\x0b\x32\x1a.tfedlrn_proto.ModelHeader\x12\x0f\n\x07results\x18\x03 \x02(\x02\x12\x11\n\tdata_size\x18\x04 \x02(\x05\"l\n\nJobRequest\x12,\n\x06header\x18\x01 \x02(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12\x30\n\x0cmodel_header\x18\x02 \x02(\x0b\x32\x1a.tfedlrn_proto.ModelHeader\"v\n\x14ModelDownloadRequest\x12,\n\x06header\x18\x01 \x02(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12\x30\n\x0cmodel_header\x18\x02 \x02(\x0b\x32\x1a.tfedlrn_proto.ModelHeader\"k\n\x11GlobalModelUpdate\x12,\n\x06header\x18\x01 \x02(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12(\n\x05model\x18\x02 \x02(\x0b\x32\x19.tfedlrn_proto.ModelProto\"Y\n\x08JobReply\x12,\n\x06header\x18\x01 \x02(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\x12\x1f\n\x03job\x18\x02 \x02(\x0e\x32\x12.tfedlrn_proto.Job\"C\n\x13LocalModelUpdateAck\x12,\n\x06header\x18\x01 \x02(\x0b\x32\x1c.tfedlrn_proto.MessageHeader\"I\n\x19LocalValidationResultsAck\x12,\n\x06header\x18\x01 \x02(\x0b\x32\x1c.tfedlrn_proto.MessageHeader*[\n\x03Job\x12\r\n\tJOB_TRAIN\x10\x00\x12\x10\n\x0cJOB_VALIDATE\x10\x01\x12\r\n\tJOB_YIELD\x10\x02\x12\x0c\n\x08JOB_QUIT\x10\x03\x12\x16\n\x12JOB_DOWNLOAD_MODEL\x10\x04')
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
  serialized_start=1743,
  serialized_end=1834,
)
_sym_db.RegisterEnumDescriptor(_JOB)

Job = enum_type_wrapper.EnumTypeWrapper(_JOB)
JOB_TRAIN = 0
JOB_VALIDATE = 1
JOB_YIELD = 2
JOB_QUIT = 3
JOB_DOWNLOAD_MODEL = 4



_FLMESSAGE = _descriptor.Descriptor(
  name='FLMessage',
  full_name='tfedlrn_proto.FLMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='localmodelupdate', full_name='tfedlrn_proto.FLMessage.localmodelupdate', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='localvalidationresults', full_name='tfedlrn_proto.FLMessage.localvalidationresults', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='jobrequest', full_name='tfedlrn_proto.FLMessage.jobrequest', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='modeldownloadrequest', full_name='tfedlrn_proto.FLMessage.modeldownloadrequest', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='globalmodelupdate', full_name='tfedlrn_proto.FLMessage.globalmodelupdate', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='jobreply', full_name='tfedlrn_proto.FLMessage.jobreply', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='localmodelupdateack', full_name='tfedlrn_proto.FLMessage.localmodelupdateack', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='localvalidationresultsack', full_name='tfedlrn_proto.FLMessage.localvalidationresultsack', index=7,
      number=8, type=11, cpp_type=10, label=1,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='payload', full_name='tfedlrn_proto.FLMessage.payload',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=39,
  serialized_end=567,
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
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='shape', full_name='tfedlrn_proto.TensorProto.shape', index=1,
      number=2, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='values', full_name='tfedlrn_proto.TensorProto.values', index=2,
      number=3, type=2, cpp_type=6, label=3,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=569,
  serialized_end=627,
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
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='recipient', full_name='tfedlrn_proto.MessageHeader.recipient', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='federation_id', full_name='tfedlrn_proto.MessageHeader.federation_id', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='counter', full_name='tfedlrn_proto.MessageHeader.counter', index=3,
      number=4, type=5, cpp_type=1, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=629,
  serialized_end=719,
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
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='tfedlrn_proto.ModelHeader.version', index=1,
      number=2, type=5, cpp_type=1, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=721,
  serialized_end=763,
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
      number=1, type=11, cpp_type=10, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=765,
  serialized_end=866,
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
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model', full_name='tfedlrn_proto.LocalModelUpdate.model', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data_size', full_name='tfedlrn_proto.LocalModelUpdate.data_size', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='loss', full_name='tfedlrn_proto.LocalModelUpdate.loss', index=3,
      number=4, type=2, cpp_type=6, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=869,
  serialized_end=1008,
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
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model_header', full_name='tfedlrn_proto.LocalValidationResults.model_header', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='results', full_name='tfedlrn_proto.LocalValidationResults.results', index=2,
      number=3, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data_size', full_name='tfedlrn_proto.LocalValidationResults.data_size', index=3,
      number=4, type=5, cpp_type=1, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1011,
  serialized_end=1167,
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
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model_header', full_name='tfedlrn_proto.JobRequest.model_header', index=1,
      number=2, type=11, cpp_type=10, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1169,
  serialized_end=1277,
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
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model_header', full_name='tfedlrn_proto.ModelDownloadRequest.model_header', index=1,
      number=2, type=11, cpp_type=10, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1279,
  serialized_end=1397,
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
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='model', full_name='tfedlrn_proto.GlobalModelUpdate.model', index=1,
      number=2, type=11, cpp_type=10, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1399,
  serialized_end=1506,
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
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='job', full_name='tfedlrn_proto.JobReply.job', index=1,
      number=2, type=14, cpp_type=8, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1508,
  serialized_end=1597,
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
      number=1, type=11, cpp_type=10, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1599,
  serialized_end=1666,
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
      number=1, type=11, cpp_type=10, label=2,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1668,
  serialized_end=1741,
)

_FLMESSAGE.fields_by_name['localmodelupdate'].message_type = _LOCALMODELUPDATE
_FLMESSAGE.fields_by_name['localvalidationresults'].message_type = _LOCALVALIDATIONRESULTS
_FLMESSAGE.fields_by_name['jobrequest'].message_type = _JOBREQUEST
_FLMESSAGE.fields_by_name['modeldownloadrequest'].message_type = _MODELDOWNLOADREQUEST
_FLMESSAGE.fields_by_name['globalmodelupdate'].message_type = _GLOBALMODELUPDATE
_FLMESSAGE.fields_by_name['jobreply'].message_type = _JOBREPLY
_FLMESSAGE.fields_by_name['localmodelupdateack'].message_type = _LOCALMODELUPDATEACK
_FLMESSAGE.fields_by_name['localvalidationresultsack'].message_type = _LOCALVALIDATIONRESULTSACK
_FLMESSAGE.oneofs_by_name['payload'].fields.append(
  _FLMESSAGE.fields_by_name['localmodelupdate'])
_FLMESSAGE.fields_by_name['localmodelupdate'].containing_oneof = _FLMESSAGE.oneofs_by_name['payload']
_FLMESSAGE.oneofs_by_name['payload'].fields.append(
  _FLMESSAGE.fields_by_name['localvalidationresults'])
_FLMESSAGE.fields_by_name['localvalidationresults'].containing_oneof = _FLMESSAGE.oneofs_by_name['payload']
_FLMESSAGE.oneofs_by_name['payload'].fields.append(
  _FLMESSAGE.fields_by_name['jobrequest'])
_FLMESSAGE.fields_by_name['jobrequest'].containing_oneof = _FLMESSAGE.oneofs_by_name['payload']
_FLMESSAGE.oneofs_by_name['payload'].fields.append(
  _FLMESSAGE.fields_by_name['modeldownloadrequest'])
_FLMESSAGE.fields_by_name['modeldownloadrequest'].containing_oneof = _FLMESSAGE.oneofs_by_name['payload']
_FLMESSAGE.oneofs_by_name['payload'].fields.append(
  _FLMESSAGE.fields_by_name['globalmodelupdate'])
_FLMESSAGE.fields_by_name['globalmodelupdate'].containing_oneof = _FLMESSAGE.oneofs_by_name['payload']
_FLMESSAGE.oneofs_by_name['payload'].fields.append(
  _FLMESSAGE.fields_by_name['jobreply'])
_FLMESSAGE.fields_by_name['jobreply'].containing_oneof = _FLMESSAGE.oneofs_by_name['payload']
_FLMESSAGE.oneofs_by_name['payload'].fields.append(
  _FLMESSAGE.fields_by_name['localmodelupdateack'])
_FLMESSAGE.fields_by_name['localmodelupdateack'].containing_oneof = _FLMESSAGE.oneofs_by_name['payload']
_FLMESSAGE.oneofs_by_name['payload'].fields.append(
  _FLMESSAGE.fields_by_name['localvalidationresultsack'])
_FLMESSAGE.fields_by_name['localvalidationresultsack'].containing_oneof = _FLMESSAGE.oneofs_by_name['payload']
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
_GLOBALMODELUPDATE.fields_by_name['header'].message_type = _MESSAGEHEADER
_GLOBALMODELUPDATE.fields_by_name['model'].message_type = _MODELPROTO
_JOBREPLY.fields_by_name['header'].message_type = _MESSAGEHEADER
_JOBREPLY.fields_by_name['job'].enum_type = _JOB
_LOCALMODELUPDATEACK.fields_by_name['header'].message_type = _MESSAGEHEADER
_LOCALVALIDATIONRESULTSACK.fields_by_name['header'].message_type = _MESSAGEHEADER
DESCRIPTOR.message_types_by_name['FLMessage'] = _FLMESSAGE
DESCRIPTOR.message_types_by_name['TensorProto'] = _TENSORPROTO
DESCRIPTOR.message_types_by_name['MessageHeader'] = _MESSAGEHEADER
DESCRIPTOR.message_types_by_name['ModelHeader'] = _MODELHEADER
DESCRIPTOR.message_types_by_name['ModelProto'] = _MODELPROTO
DESCRIPTOR.message_types_by_name['LocalModelUpdate'] = _LOCALMODELUPDATE
DESCRIPTOR.message_types_by_name['LocalValidationResults'] = _LOCALVALIDATIONRESULTS
DESCRIPTOR.message_types_by_name['JobRequest'] = _JOBREQUEST
DESCRIPTOR.message_types_by_name['ModelDownloadRequest'] = _MODELDOWNLOADREQUEST
DESCRIPTOR.message_types_by_name['GlobalModelUpdate'] = _GLOBALMODELUPDATE
DESCRIPTOR.message_types_by_name['JobReply'] = _JOBREPLY
DESCRIPTOR.message_types_by_name['LocalModelUpdateAck'] = _LOCALMODELUPDATEACK
DESCRIPTOR.message_types_by_name['LocalValidationResultsAck'] = _LOCALVALIDATIONRESULTSACK
DESCRIPTOR.enum_types_by_name['Job'] = _JOB
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FLMessage = _reflection.GeneratedProtocolMessageType('FLMessage', (_message.Message,), dict(
  DESCRIPTOR = _FLMESSAGE,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.FLMessage)
  ))
_sym_db.RegisterMessage(FLMessage)

TensorProto = _reflection.GeneratedProtocolMessageType('TensorProto', (_message.Message,), dict(
  DESCRIPTOR = _TENSORPROTO,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.TensorProto)
  ))
_sym_db.RegisterMessage(TensorProto)

MessageHeader = _reflection.GeneratedProtocolMessageType('MessageHeader', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGEHEADER,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.MessageHeader)
  ))
_sym_db.RegisterMessage(MessageHeader)

ModelHeader = _reflection.GeneratedProtocolMessageType('ModelHeader', (_message.Message,), dict(
  DESCRIPTOR = _MODELHEADER,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.ModelHeader)
  ))
_sym_db.RegisterMessage(ModelHeader)

ModelProto = _reflection.GeneratedProtocolMessageType('ModelProto', (_message.Message,), dict(
  DESCRIPTOR = _MODELPROTO,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.ModelProto)
  ))
_sym_db.RegisterMessage(ModelProto)

LocalModelUpdate = _reflection.GeneratedProtocolMessageType('LocalModelUpdate', (_message.Message,), dict(
  DESCRIPTOR = _LOCALMODELUPDATE,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.LocalModelUpdate)
  ))
_sym_db.RegisterMessage(LocalModelUpdate)

LocalValidationResults = _reflection.GeneratedProtocolMessageType('LocalValidationResults', (_message.Message,), dict(
  DESCRIPTOR = _LOCALVALIDATIONRESULTS,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.LocalValidationResults)
  ))
_sym_db.RegisterMessage(LocalValidationResults)

JobRequest = _reflection.GeneratedProtocolMessageType('JobRequest', (_message.Message,), dict(
  DESCRIPTOR = _JOBREQUEST,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.JobRequest)
  ))
_sym_db.RegisterMessage(JobRequest)

ModelDownloadRequest = _reflection.GeneratedProtocolMessageType('ModelDownloadRequest', (_message.Message,), dict(
  DESCRIPTOR = _MODELDOWNLOADREQUEST,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.ModelDownloadRequest)
  ))
_sym_db.RegisterMessage(ModelDownloadRequest)

GlobalModelUpdate = _reflection.GeneratedProtocolMessageType('GlobalModelUpdate', (_message.Message,), dict(
  DESCRIPTOR = _GLOBALMODELUPDATE,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.GlobalModelUpdate)
  ))
_sym_db.RegisterMessage(GlobalModelUpdate)

JobReply = _reflection.GeneratedProtocolMessageType('JobReply', (_message.Message,), dict(
  DESCRIPTOR = _JOBREPLY,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.JobReply)
  ))
_sym_db.RegisterMessage(JobReply)

LocalModelUpdateAck = _reflection.GeneratedProtocolMessageType('LocalModelUpdateAck', (_message.Message,), dict(
  DESCRIPTOR = _LOCALMODELUPDATEACK,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.LocalModelUpdateAck)
  ))
_sym_db.RegisterMessage(LocalModelUpdateAck)

LocalValidationResultsAck = _reflection.GeneratedProtocolMessageType('LocalValidationResultsAck', (_message.Message,), dict(
  DESCRIPTOR = _LOCALVALIDATIONRESULTSACK,
  __module__ = 'proto.message_pb2'
  # @@protoc_insertion_point(class_scope:tfedlrn_proto.LocalValidationResultsAck)
  ))
_sym_db.RegisterMessage(LocalValidationResultsAck)


# @@protoc_insertion_point(module_scope)
