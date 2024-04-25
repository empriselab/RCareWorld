import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


def parse_message(msg: IncomingMessage) -> dict:
    """
    Writes 8 new entries to the dictionary:

    `[left or right]_[upper or fore]arm_hole_likelihood`, corresponding to the score rating for how likely it is that the arm is actually in the hole.

    `[left or right]_[upper or fore]arm_distance`, corresponding to the distance between the arm and the hole. -1 corresponds to the hole being just on the entering edge of the arm. 1 corresponds to it being just on the exit edge of the arm. Not clamped.

    Returns the modified dictionary.
    """
    this_object_data = attr.base_attr.parse_message(msg)

    # Get scoring info
    right_forearm_hole_likelihood = msg.read_float32()
    right_upperarm_hole_likelihood = msg.read_float32()
    left_forearm_hole_likelihood = msg.read_float32()
    left_upperarm_hole_likelihood = msg.read_float32()

    this_object_data["right_forearm_hole_likelihood"] = right_forearm_hole_likelihood
    this_object_data["right_upperarm_hole_likelihood"] = right_upperarm_hole_likelihood
    this_object_data["left_forearm_hole_likelihood"] = left_forearm_hole_likelihood
    this_object_data["left_upperarm_hole_likelihood"] = left_upperarm_hole_likelihood

    right_forearm_distance = msg.read_float32()
    right_upperarm_distance = msg.read_float32()
    left_forearm_distance = msg.read_float32()
    left_upperarm_distance = msg.read_float32()

    this_object_data["right_forearm_distance"] = right_forearm_distance
    this_object_data["right_upperarm_distance"] = right_upperarm_distance
    this_object_data["left_forearm_distance"] = left_forearm_distance
    this_object_data["left_upperarm_distance"] = left_upperarm_distance

    return this_object_data


def score_forces(data: dict) -> float:
    """
    Scores a set of data in the form of a dictionary returned by parse_message.

    Feel free to change.
    """
    left_arm_distance_score = 0
    right_arm_distance_score = 0
    if data["left_forearm_distance"] > -1 and data["left_forearm_distance"] < 1:
        left_arm_distance_score = (data["left_forearm_distance"] + 1) / 2
    elif data["left_upperarm_distance"] > -1 and data["left_upperarm_distance"] < 1:
        left_arm_distance_score = (data["left_upperarm_distance"] + 1) / 2
        left_arm_distance_score += 1

    if data["right_forearm_distance"] > -1 and data["right_forearm_distance"] < 1:
        right_arm_distance_score = (data["right_forearm_distance"] + 1) / 2
    elif data["right_upperarm_distance"] > -1 and data["right_upperarm_distance"] < 1:
        right_arm_distance_score = (data["right_upperarm_distance"] + 1) / 2
        right_arm_distance_score += 1

    left_likelihood = max(
        data["left_forearm_hole_likelihood"], data["left_upperarm_hole_likelihood"]
    )
    right_likelihood = max(
        data["right_forearm_hole_likelihood"], data["right_upperarm_hole_likelihood"]
    )

    return (
        left_arm_distance_score * left_likelihood
        + right_arm_distance_score * right_likelihood
    )
