import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = attr.base_attr.parse_message(msg)
    this_object_data["move_done"] = msg.read_bool()
    this_object_data["rotate_done"] = msg.read_bool()
    return this_object_data


def HumanIKTargetDoMove(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "index", "position", "duration"]
    optional_params = ["speed_based", "relative"]
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("HumanIKTargetDoMove")
    msg.write_int32(kwargs["index"])
    msg.write_float32(kwargs["position"][0])
    msg.write_float32(kwargs["position"][1])
    msg.write_float32(kwargs["position"][2])
    msg.write_float32(kwargs["duration"])
    if "speed_based" in kwargs:
        msg.write_bool(kwargs["speed_based"])
    else:
        msg.write_bool(True)
    if "relative" in kwargs:
        msg.write_bool(kwargs["relative"])
    else:
        msg.write_bool(False)
    return msg


def HumanIKTargetDoRotate(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "index", "vector3", "duration"]
    optional_params = ["speed_based", "relative"]
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("HumanIKTargetDoRotateQuaternion")
    msg.write_int32(kwargs["index"])
    msg.write_float32(kwargs["vector3"][0])
    msg.write_float32(kwargs["vector3"][1])
    msg.write_float32(kwargs["vector3"][2])
    msg.write_float32(kwargs["duration"])
    if "speed_based" in kwargs:
        msg.write_bool(kwargs["speed_based"])
    else:
        msg.write_bool(True)
    if "relative" in kwargs:
        msg.write_bool(kwargs["relative"])
    else:
        msg.write_bool(False)
    return msg


def HumanIKTargetDoRotateQuaternion(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "index", "quaternion", "duration"]
    optional_params = ["speed_based", "relative"]
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("HumanIKTargetDoRotateQuaternion")
    msg.write_int32(kwargs["index"])
    msg.write_float32(kwargs["quaternion"][0])
    msg.write_float32(kwargs["quaternion"][1])
    msg.write_float32(kwargs["quaternion"][2])
    msg.write_float32(kwargs["quaternion"][3])
    msg.write_float32(kwargs["duration"])
    if "speed_based" in kwargs:
        msg.write_bool(kwargs["speed_based"])
    else:
        msg.write_bool(True)
    if "relative" in kwargs:
        msg.write_bool(kwargs["relative"])
    else:
        msg.write_bool(False)
    return msg


def HumanIKTargetDoComplete(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "index"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("HumanIKTargetDoComplete")
    msg.write_int32(kwargs["index"])
    return msg


def HumanIKTargetDoKill(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "index"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("HumanIKTargetDoKill")
    msg.write_int32(kwargs["index"])
    return msg
