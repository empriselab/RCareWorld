from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = {}
    this_object_data["name"] = msg.read_string()
    this_object_data["position"] = [msg.read_float32() for _ in range(3)]
    this_object_data["rotation"] = [msg.read_float32() for _ in range(3)]
    this_object_data["quaternion"] = [msg.read_float32() for _ in range(4)]
    this_object_data["local_position"] = [msg.read_float32() for _ in range(3)]
    this_object_data["local_rotation"] = [msg.read_float32() for _ in range(3)]
    this_object_data["local_quaternion"] = [msg.read_float32() for _ in range(4)]
    this_object_data["local_to_world_matrix"] = msg.read_float32_list()
    if msg.read_bool() is True:
        this_object_data["result_local_point"] = msg.read_float32_list()
    if msg.read_bool() is True:
        this_object_data["result_world_point"] = msg.read_float32_list()
    return this_object_data


def SetTransform(kwargs: dict) -> OutgoingMessage:
    """Set the transform of a object, specified by id.
    Args:
        Compulsory:
        id: The id of object.

        Optional:
        position: A 3-d list inferring object's position, in [x,y,z] order.
        rotation: A 3-d list inferring object's rotation, in [x,y,z] order.
        scale: A 3-d list inferring object's rotation, in [x,y,z] order.
    """
    compulsory_params = ["id"]
    optional_params = ["position", "rotation", "scale", "is_world"]
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("SetTransform")
    position = None
    set_position = False
    rotation = None
    set_rotation = False
    scale = None
    set_scale = False

    if "position" in kwargs:  # position
        position = kwargs["position"]
        set_position = True
        assert (
            type(position) == list and len(position) == 3
        ), "Argument position must be a 3-d list."

    if "rotation" in kwargs:  # rotation
        rotation = kwargs["rotation"]
        set_rotation = True
        assert (
            type(rotation) == list and len(rotation) == 3
        ), "Argument rotation must be a 3-d list."

    if "scale" in kwargs:  # scale
        scale = kwargs["scale"]
        set_scale = True
        assert (
            type(scale) == list and len(scale) == 3
        ), "Argument rotation must be a 3-d list."

    msg.write_bool(set_position)
    msg.write_bool(set_rotation)
    msg.write_bool(set_scale)

    if set_position:
        for i in range(3):
            msg.write_float32(position[i])

    if set_rotation:
        for i in range(3):
            msg.write_float32(rotation[i])

    if set_scale:
        for i in range(3):
            msg.write_float32(scale[i])

    if "is_world" in kwargs.keys():
        msg.write_bool(kwargs["is_world"])
    else:
        msg.write_bool(True)
    return msg


def SetRotationQuaternion(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "quaternion"]
    optional_params = ["is_world"]
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()
    msg.write_int32(kwargs["id"])
    msg.write_string("SetRotationQuaternion")
    for i in range(4):
        msg.write_float32(kwargs["quaternion"][i])
    if "is_world" in kwargs.keys():
        msg.write_bool(kwargs["is_world"])
    else:
        msg.write_bool(True)
    return msg


def SetActive(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "active"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("SetActive")
    msg.write_bool(kwargs["active"])

    return msg


def SetParent(kwargs: dict) -> OutgoingMessage:
    """Set parent of a object inferred by the id
    Args:
        Compulsory:
        id: The id of object, specified in returned message.
        parent_id: The id of parent object
        parent_name: The name of parent object
    """
    compulsory_params = ["id", "parent_id", "parent_name"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("SetParent")
    msg.write_int32(kwargs["parent_id"])
    msg.write_string(kwargs["parent_name"])

    return msg


def SetLayer(kwargs: dict) -> OutgoingMessage:
    """Set layer of a object inferred by the id
    Args:
        Compulsory:
        id: The id of object, specified in returned message.
        layer: The layer of object
    """
    compulsory_params = ["id", "layer"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("SetLayer")
    msg.write_int32(kwargs["layer"])

    return msg


def Copy(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "copy_id"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("Copy")
    msg.write_int32(kwargs["copy_id"])
    return msg


def Destroy(kwargs: dict) -> OutgoingMessage:
    """Destroy a object inferred by the id
    Args:
        Compulsory:
        id: The id of object, specified in returned message.
    """
    compulsory_params = ["id"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("Destroy")

    return msg


def GetLoaclPointFromWorld(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "point"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("GetLoaclPointFromWorld")
    msg.write_float32(kwargs["point"][0])
    msg.write_float32(kwargs["point"][1])
    msg.write_float32(kwargs["point"][2])
    return msg


def GetWorldPointFromLocal(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "point"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("GetWorldPointFromLocal")
    msg.write_float32(kwargs["point"][0])
    msg.write_float32(kwargs["point"][1])
    msg.write_float32(kwargs["point"][2])
    return msg
