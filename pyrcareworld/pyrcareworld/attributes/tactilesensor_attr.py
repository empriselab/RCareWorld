import numpy as np

import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = attr.base_attr.parse_message(msg)
    this_object_data["forces"] = msg.read_float32_list()
    this_object_data["positions"] = (
        np.array(msg.read_float32_list()).reshape(-1, 3).tolist()
    )
    # TODO: Add normal vectors
    count = msg.read_int32()
    this_object_data["ids"] = [msg.read_int32() for _ in range(count)]
    return this_object_data
