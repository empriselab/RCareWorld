import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    this_object_data = attr.base_attr.parse_message(msg)
    return this_object_data


def AddParticleAnchor(kwargs: dict) -> OutgoingMessage:
    """
    Sends a message containing a request to add a particle anchor to the cloth actor for the specified particle group and anchored to the object given by anchor_id.
    """
    compulsory_params = ["id", "particle_group_name", "anchor_id"]
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("AddParticleAnchor")

    msg.write_string(kwargs["particle_group_name"])
    msg.write_int32(kwargs["anchor_id"])

    return msg


def RemoveParticleAnchor(kwargs: dict) -> OutgoingMessage:
    """
    Sends a message containing a request to remove a particle anchor from the cloth actor for the specified particle group. Removes ALL anchors for the particle group.
    """
    compulsory_params = ["id", "particle_group_name"]
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("RemoveParticleAnchor")

    msg.write_string(kwargs["particle_group_name"])

    return msg
