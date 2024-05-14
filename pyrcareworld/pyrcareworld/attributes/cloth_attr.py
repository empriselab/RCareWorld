import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    """
    Fetches the same information as a base_attr, but with the additional
    `"particle_groups"` key. You can do `dict["particle_groups"][particle_group_name]` to get the list of positions, which are each represented as a 3-length list.

    Returns:
        dict: The same information as base_attr, but with the additional
        `"particle_groups"` key.
    """
    this_object_data = attr.base_attr.parse_message(msg)
    count = msg.read_int32()
    this_object_data["particle_groups"] = {}
    for _ in range(count):
        # First is the particle group name.
        name = msg.read_string()
        # Finally is the xs list, then the ys list, then the zs list.
        xs = msg.read_float32_list()
        ys = msg.read_float32_list()
        zs = msg.read_float32_list()

        # Make a couple of lists
        positions = [[x, y, z] for x, y, z in zip(xs, ys, zs)]

        this_object_data["particle_groups"][name] = positions

    has_forces = msg.read_bool()
    this_object_data["forces"] = []

    if has_forces:
        x = msg.read_float32()
        y = msg.read_float32()
        z = msg.read_float32()
        this_object_data["forces"] = [x, y, z]

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


def InitializeParticlePositions(kwargs: dict) -> OutgoingMessage:
    """
    Sends a message containing a mapping from particle indices to their initial positions. Particles will teleport to this position when this function is called.
    """
    compulsory_params = ["id", "particle_indices", "positions"]
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("InitializeParticlePositions")
    # Float list of particle indices. May assume all integers.
    msg.write_float32_list(kwargs["particle_indices"])

    # Extract X, Y, and Z from positions into separate lists.
    xs = [p[0] for p in kwargs["positions"]]
    ys = [p[1] for p in kwargs["positions"]]
    zs = [p[2] for p in kwargs["positions"]]

    # Send x, then y, then z.
    msg.write_float32_list(xs)
    msg.write_float32_list(ys)
    msg.write_float32_list(zs)

    return msg


def FetchParticlePositions(kwargs: dict) -> OutgoingMessage:
    """
    Sends a message containing a request to fetch the current positions of all particles in the cloth actor for the specified particle group.
    """
    compulsory_params = ["id", "particle_group_name"]
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()

    msg.write_int32(kwargs["id"])
    msg.write_string("FetchParticlePositions")

    msg.write_string(kwargs["particle_group_name"])

    return msg
