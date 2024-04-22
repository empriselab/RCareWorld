import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    """
    Adds a new dictionary entry `"forces"` that contains the forces acting on the sponge. May contain no forces if the sponge is not currently being pushed.

    Also populates `"proportion"` with the proportion of the texture that is painted, or None if no proportion is available.
    """
    this_object_data = attr.base_attr.parse_message(msg)
    count = msg.read_int32()
    this_object_data["forces"] = []
    if count > 0:
        this_object_data["forces"] = msg.read_float32_list()
    has_proportion = msg.read_bool()
    this_object_data["proportion"] = None
    if has_proportion:
        this_object_data["proportion"] = msg.read_float32()
    return this_object_data


def score_forces(forces: list) -> float:
    """
    Given a list of forces, returns a score for it between 0 and 1, 1 being
    perfect. If an empty list is input, 0 is returned.
    """
    if len(forces) == 0:
        return 0
    # Currently implemented with a simple heuristic that returns the
    # proportion of forces in a threshold.
    lower = 0
    upper = 200

    num_within = 0
    for force in forces:
        if force > lower and force < upper:
            num_within += 1
    return num_within / len(forces)
