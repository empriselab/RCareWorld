import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = attr.base_attr.parse_message(msg)
    return this_object_data


def GenerateVHACDColider(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("GenerateVHACDColider")
    return msg
