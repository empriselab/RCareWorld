import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility

def parse_message(msg: IncomingMessage) -> dict:
    """
    Parses messages received from Unity with more detailed metrics and additional data points.
    """
    this_object_data = attr.base_attr.parse_message(msg)

    # Get detailed scoring info
    right_forearm_hole_likelihood = msg.read_float32()
    right_upperarm_hole_likelihood = msg.read_float32()
    left_forearm_hole_likelihood = msg.read_float32()
    left_upperarm_hole_likelihood = msg.read_float32()

    # Populate the dictionary with hole likelihood scores
    this_object_data.update({
        "right_forearm_hole_likelihood": right_forearm_hole_likelihood,
        "right_upperarm_hole_likelihood": right_upperarm_hole_likelihood,
        "left_forearm_hole_likelihood": left_forearm_hole_likelihood,
        "left_upperarm_hole_likelihood": left_upperarm_hole_likelihood
    })

    # Read distance metrics
    right_forearm_distance = msg.read_float32()
    right_upperarm_distance = msg.read_float32()
    left_forearm_distance = msg.read_float32()
    left_upperarm_distance = msg.read_float32()

    # Populate the dictionary with distance scores
    this_object_data.update({
        "right_forearm_distance": right_forearm_distance,
        "right_upperarm_distance": right_upperarm_distance,
        "left_forearm_distance": left_forearm_distance,
        "left_upperarm_distance": left_upperarm_distance
    })

    # New data points for shoulder and overall arm coverage
    shoulder_coverage = msg.read_float32()
    right_arm_coverage = msg.read_float32()
    left_arm_coverage = msg.read_float32()

    # Populate the dictionary with coverage scores
    this_object_data.update({
        "shoulder_coverage": shoulder_coverage,
        "right_arm_coverage": right_arm_coverage,
        "left_arm_coverage": left_arm_coverage
    })

    return this_object_data

def score_forces(data: dict) -> float:
    """
    Revised scoring mechanism that factors in both distance and hole likelihood, 
    and adds consideration for shoulder and overall arm coverage.
    """
    # Calculate distance scores considering both forearm and upper arm
    left_arm_distance_score = utility.calculate_score(data["left_forearm_distance"], data["left_upperarm_distance"])
    right_arm_distance_score = utility.calculate_score(data["right_forearm_distance"], data["right_upperarm_distance"])

    # Calculate the maximum likelihood for each arm being in the hole
    left_likelihood = max(data["left_forearm_hole_likelihood"], data["left_upperarm_hole_likelihood"])
    right_likelihood = max(data["right_forearm_hole_likelihood"], data["right_upperarm_hole_likelihood"])

    # Calculate the coverage score, factoring in both shoulders and arms
    coverage_score = data["shoulder_coverage"] + data["right_arm_coverage"] + data["left_arm_coverage"]

    # Calculate the overall score
    overall_score = (
        left_arm_distance_score * left_likelihood +
        right_arm_distance_score * right_likelihood +
        coverage_score
    )

    return overall_score

if __name__ == "__main__":
    # Example usage
    msg = IncomingMessage(data=b'Your binary data here')
    data_dict = parse_message(msg)
    score = score_forces(data_dict)
    print("Calculated Score:", score)



# import pyrcareworld.attributes as attr
# from pyrcareworld.side_channel.side_channel import (
#     IncomingMessage,
#     OutgoingMessage,
# )
# import pyrcareworld.utils.utility as utility


# def parse_message(msg: IncomingMessage) -> dict:
#     """
#     Writes 8 new entries to the dictionary:

#     `[left or right]_[upper or fore]arm_hole_likelihood`, corresponding to the score rating for how likely it is that the arm is actually in the hole.

#     `[left or right]_[upper or fore]arm_distance`, corresponding to the distance between the arm and the hole. -1 corresponds to the hole being just on the entering edge of the arm. 1 corresponds to it being just on the exit edge of the arm. Not clamped.

#     Returns the modified dictionary.
#     """
#     this_object_data = attr.base_attr.parse_message(msg)

#     # Get scoring info
#     right_forearm_hole_likelihood = msg.read_float32()
#     right_upperarm_hole_likelihood = msg.read_float32()
#     left_forearm_hole_likelihood = msg.read_float32()
#     left_upperarm_hole_likelihood = msg.read_float32()

#     this_object_data["right_forearm_hole_likelihood"] = right_forearm_hole_likelihood
#     this_object_data["right_upperarm_hole_likelihood"] = right_upperarm_hole_likelihood
#     this_object_data["left_forearm_hole_likelihood"] = left_forearm_hole_likelihood
#     this_object_data["left_upperarm_hole_likelihood"] = left_upperarm_hole_likelihood

#     right_forearm_distance = msg.read_float32()
#     right_upperarm_distance = msg.read_float32()
#     left_forearm_distance = msg.read_float32()
#     left_upperarm_distance = msg.read_float32()

#     this_object_data["right_forearm_distance"] = right_forearm_distance
#     this_object_data["right_upperarm_distance"] = right_upperarm_distance
#     this_object_data["left_forearm_distance"] = left_forearm_distance
#     this_object_data["left_upperarm_distance"] = left_upperarm_distance

#     return this_object_data


# def score_forces(data: dict) -> float:
#     """
#     Scores a set of data in the form of a dictionary returned by parse_message.

#     Feel free to change.
#     """
#     left_arm_distance_score = 0
#     right_arm_distance_score = 0
#     if data["left_forearm_distance"] > -1 and data["left_forearm_distance"] < 1:
#         left_arm_distance_score = (data["left_forearm_distance"] + 1) / 2
#     elif data["left_upperarm_distance"] > -1 and data["left_upperarm_distance"] < 1:
#         left_arm_distance_score = (data["left_upperarm_distance"] + 1) / 2
#         left_arm_distance_score += 1

#     if data["right_forearm_distance"] > -1 and data["right_forearm_distance"] < 1:
#         right_arm_distance_score = (data["right_forearm_distance"] + 1) / 2
#     elif data["right_upperarm_distance"] > -1 and data["right_upperarm_distance"] < 1:
#         right_arm_distance_score = (data["right_upperarm_distance"] + 1) / 2
#         right_arm_distance_score += 1

#     left_likelihood = max(
#         data["left_forearm_hole_likelihood"], data["left_upperarm_hole_likelihood"]
#     )
#     right_likelihood = max(
#         data["right_forearm_hole_likelihood"], data["right_upperarm_hole_likelihood"]
#     )

#     return (
#         left_arm_distance_score * left_likelihood
#         + right_arm_distance_score * right_likelihood
#     )
