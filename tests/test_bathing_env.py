"""Tests for the bathing environment.

NOTE: run this file with pytest -s tests/test_bathing_env.py.
"""

from pyrcareworld.envs.bathing_env import BathingEnv

import pytest
import numpy as np


def degrees_to_radians(angle):
    """Convert from degrees to radians."""
    return np.pi * angle / 180

def wrap_angle(angle):
    """Wrap an angle in radians to [-pi, pi]."""
    return np.arctan2(np.sin(angle), np.cos(angle))


def get_signed_angle_distance(target, source):
    """Given two angles between [-pi, pi], get the smallest signed angle d s.t.

    source + d = target.
    """
    assert -np.pi <= source <= np.pi
    assert -np.pi <= target <= np.pi
    a = target - source
    return (a + np.pi) % (2 * np.pi) - np.pi


def euler_angles_allclose(euler1, euler2, atol = 1e-6):
    """Compare two euler angles."""
    wrapped_angles1 = [wrap_angle(degrees_to_radians(a)) for a in euler1]
    wrapped_angles2 = [wrap_angle(degrees_to_radians(a)) for a in euler2]
    dists = [get_signed_angle_distance(a, b)
             for a, b in zip(wrapped_angles1, wrapped_angles2)]
    return np.allclose(dists, 0, atol=atol)


@pytest.fixture(scope="session", name="bathing_env", autouse=True)
def _bathing_env_fixture():
    """Create a BathingEnv once and share it across tests."""
    # NOTE: set graphics = True here to debug.
    env = BathingEnv(graphics=False)    
    yield env
    env.close()


def test_bathing_stretch_move_commands(bathing_env):
    """Tests for turning and moving the stretch base in the bathing env."""

    num_steps_per_command = 300
    robot = bathing_env.get_robot()

    # Move forward.
    robot_base_position = robot.data["positions"][0].copy()
    robot.MoveForward(0.5, 0.5)
    bathing_env.step(num_steps_per_command)
    new_robot_base_position = robot.data["positions"][0].copy()
    expected_robot_base_position = np.add(robot_base_position, (0, 0, 0.5))
    # NOTE: moving is not precise beyond ~0.25. Users may want to build a controller
    # on top to compensate.
    assert np.allclose(new_robot_base_position, expected_robot_base_position, atol=0.25)

    # Move backward.
    robot_base_position = robot.data["positions"][0].copy()
    robot.MoveBack(0.5, 0.5)
    bathing_env.step(num_steps_per_command)
    new_robot_base_position = robot.data["positions"][0].copy()
    expected_robot_base_position = np.add(robot_base_position, (0, 0, -0.5))
    assert np.allclose(new_robot_base_position, expected_robot_base_position, atol=0.25)

    # Turn left.
    robot_base_rotation = robot.data["rotations"][0].copy()
    robot.TurnLeft(90, 1)  # turn the robot left 90 degrees with a speed of 1.
    bathing_env.step(num_steps_per_command)  # long enough for the full turn
    # The yaw should have changed by about 90 degrees.
    new_robot_base_rotation = robot.data["rotations"][0].copy()
    expected_robot_base_rotation = np.add(robot_base_rotation, (0.0, 0.0, 90.0))
    # NOTE: turning is not precise beyond ~5 degrees. Users may want to build a controller
    # on top to compensate.
    assert euler_angles_allclose(new_robot_base_rotation, expected_robot_base_rotation, atol=5.0)

    # Turn right.
    robot_base_rotation = robot.data["rotations"][0].copy()
    robot.TurnRight(90, 1)
    bathing_env.step(num_steps_per_command)
    new_robot_base_rotation = robot.data["rotations"][0].copy()
    expected_robot_base_rotation = np.add(robot_base_rotation, (0.0, 0.0, -90.0))
    assert euler_angles_allclose(new_robot_base_rotation, expected_robot_base_rotation, atol=5.0)
