import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    """
    Adds a new dictionary entry `"forces"` that contains the forces acting on the sponge. May contain no forces if the sponge is not currently being pushed.
    """
    this_object_data = attr.base_attr.parse_message(msg)
    count = msg.read_int32()
    this_object_data["forces"] = []
    if count > 0:
        this_object_data["forces"] = msg.read_float32_list()
    return this_object_data
