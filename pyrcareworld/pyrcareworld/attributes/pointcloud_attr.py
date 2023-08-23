import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = {}
    return this_object_data


def ShowPointCloud(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "positions", "colors"]
    optional_params = ["radius"]
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()
    if "radius" not in kwargs:
        kwargs["radius"] = 0.01
    msg.write_int32(kwargs["id"])
    msg.write_string("ShowPointCloud")
    msg.write_float32_list(kwargs["positions"])
    msg.write_float32_list(kwargs["colors"])
    msg.write_float32(kwargs["radius"])
    return msg


def SetRadius(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "radius"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("SetRadius")
    msg.write_float32(kwargs["radius"])
    return msg
