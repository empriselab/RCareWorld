import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = attr.base_attr.parse_message(msg)
    return this_object_data


def Translate(kwargs: dict) -> OutgoingMessage:
    """Translate a game object by a given distance, in meter format. Note that this command will translate the
       object relative to the current position.
    Args:
        Compulsory:
        index: The index of object, specified in returned message.
        translation: A 3-d list inferring the relative translation, in [x,y,z] order.
    """
    compulsory_params = ["id", "translation"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("Translate")
    for i in range(3):
        msg.write_float32(kwargs["translation"][i])

    return msg


def Rotate(kwargs: dict) -> OutgoingMessage:
    """Rotate a game object by a given rotation, in euler angle format. Note that this command will rotate the
       object relative to the current state. The rotation order will be z axis first, x axis next, and z axis last.
    Args:
        Compulsory:
        index: The index of object, specified in returned message.
        rotation: A 3-d list inferring the relative rotation, in [x,y,z] order.
    """
    compulsory_params = ["id", "rotation"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("Rotate")
    for i in range(3):
        msg.write_float32(kwargs["rotation"][i])

    return msg


def SetColor(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "color"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("SetColor")
    for i in range(4):
        msg.write_float32(kwargs["color"][i])

    return msg
