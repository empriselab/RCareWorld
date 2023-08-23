import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = attr.collider_attr.parse_message(msg)
    this_object_data["velocity"] = [msg.read_float32() for i in range(3)]
    this_object_data["angular_vel"] = [msg.read_float32() for i in range(3)]
    return this_object_data


def SetMass(kwargs: dict) -> OutgoingMessage:
    compulsory_params = ["id", "mass"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("SetMass")
    msg.write_float32(kwargs["mass"])

    return msg


def AddForce(kwargs: dict) -> OutgoingMessage:
    """Add a constant force on a rigidbody. The rigidbody must be loaded into the scene and
    is distinguished by index.
    Args:
        Compulsory:
        id: The index of rigidbody, specified in returned message.
        force: A 3-d list inferring the force, in [x,y,z] order.
    """
    compulsory_params = ["id", "force"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)
    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("AddForce")
    msg.write_float32(kwargs["force"][0])
    msg.write_float32(kwargs["force"][1])
    msg.write_float32(kwargs["force"][2])

    return msg


def SetVelocity(kwargs: dict) -> OutgoingMessage:
    """Set the velocity of a rigidbody. The rigidbody must be loaded into the scene and
    is distinguished by index.
    Args:
        Compulsory:
        id: The index of rigidbody, specified in returned message.
        velocity: A 3-d float list inferring the velocity, in [x,y,z] order.
    """
    compulsory_params = ["index", "velocity"]
    optional_params = []
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("SetVelocity")
    msg.write_float32(kwargs["velocity"][0])
    msg.write_float32(kwargs["velocity"][1])
    msg.write_float32(kwargs["velocity"][2])

    return msg
