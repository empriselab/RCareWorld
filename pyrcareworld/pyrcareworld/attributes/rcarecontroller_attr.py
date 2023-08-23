import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility
import base64


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = attr.controller_attr.parse_message(msg)
    this_object_data["joint_accelerations"] = msg.read_float32_list()
