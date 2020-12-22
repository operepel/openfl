# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""FLedge common object types."""

from collections import namedtuple

TensorKey = namedtuple('TensorKey', ['tensor_name', 'origin', 'round_number', 'report', 'tags'])
TaskResultKey = namedtuple('TaskResultKey', ['task_name', 'owner', 'round_number'])
