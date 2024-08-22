from pyrcareworld.envs.base_env import RCareWorld
import numpy as np
import math


def average_interpolate_with_max_step_length(
    start: np.ndarray, terminal: np.ndarray, max_step_length
):
    assert start.shape == terminal.shape
    distance = terminal - start
    num_steps = int(abs(distance).max() / max_step_length) + 1
    unit = distance / num_steps

    intermediate_nodes = []
    for i in range(num_steps):
        intermediate_nodes.append(start + unit * (i + 1))
    intermediate_nodes.append(terminal)

    return np.array(intermediate_nodes)


def average_interpolate(start: np.ndarray, terminal: np.ndarray, num_steps):
    assert start.shape == terminal.shape
    distance = terminal - start
    unit = distance / num_steps

    intermediate_nodes = []
    for i in range(num_steps):
        intermediate_nodes.append(start + unit * (i + 1))

    return np.array(intermediate_nodes)


def sine_interpolate(start: np.ndarray, terminal: np.ndarray, num_steps):
    assert start.shape == terminal.shape
    distance = terminal - start

    intermediate_nodes = []
    for i in range(num_steps):
        step = (
            distance / 2 * (math.sin(math.pi / num_steps * (i + 1) - math.pi / 2) + 1)
        )
        node = start + step
        intermediate_nodes.append(node)

    return np.array(intermediate_nodes)


def rotate_by_y_axis_interpolate(
    start: np.array, center: np.array, moving_degree: float, num_steps: int
):
    """
    The rotation is default to be anti-clockwise.
    Args:
        start: The start position in Unity.
        center: The center position in Unity.
        moving_degree: The amount of rotation need to rotate, in degree.
        num_steps: The number of steps of this movement.

    Returns:
        The interpolated positions of this movement, in `np.ndarray` format
    """
    start_2d = np.array([start[0], start[2]])
    center_2d = np.array([center[0], center[2]])
    relative_2d = start_2d - center_2d
    radius = np.linalg.norm(relative_2d)
    init_radius = math.acos(float(relative_2d[0]) / radius)
    if float(relative_2d[1]) < 0:
        init_radius = -1 * init_radius
    delta_radius = moving_degree * math.pi / 180 / num_steps
    intermediate_nodes = []
    for i in range(num_steps):
        curr_target_radius = init_radius + delta_radius * (i + 1)
        relative_x = radius * math.cos(curr_target_radius)
        relative_z = radius * math.sin(curr_target_radius)
        intermediate_node = np.array(
            [center_2d[0] + relative_x, start[1], center_2d[1] + relative_z]
        )
        intermediate_nodes.append(intermediate_node)

    return np.array(intermediate_nodes)


def joint_positions_interpolation(
    env: RCareWorld, body_id, target_joint_positions, max_step_degree=3
):
    curr_jp = np.array(env.articulation_channel.data[body_id]["joint_positions"])
    target_jp = np.array(target_joint_positions)
    return average_interpolate(curr_jp, target_jp, max_step_degree)


def pos_interpolation(
    env: RCareWorld, body_id, part_index, target_pos, max_step_length=0.05
):
    curr_pos = np.array(env.articulation_channel.data[body_id]["positions"][part_index])
    targ_pos = np.array(target_pos)
    return average_interpolate(curr_pos, targ_pos, max_step_length)
