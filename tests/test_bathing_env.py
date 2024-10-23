"""Tests for the bathing environment.

NOTE: run this file with pytest -s tests/test_bathing_env.py.
"""

from pyrcareworld.envs.bathing_env import BathingEnv

import pytest
import numpy as np

from .test_angle_functions import euler_angles_allclose


@pytest.fixture(scope="session", name="bathing_env", autouse=True)
def _bathing_env_fixture():
    """Create a BathingEnv once and share it across tests."""
    # NOTE: set graphics = True here to debug.
    env = BathingEnv(graphics=False)    
    yield env
    env.close()


def test_bathing_stretch_move_commands(bathing_env: BathingEnv):
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
    expected_robot_base_rotation = np.add(robot_base_rotation, (0.0, -90.0, 0))
    # NOTE: turning is not precise beyond ~5 degrees. Users may want to build a controller
    # on top to compensate.
    assert euler_angles_allclose(new_robot_base_rotation, expected_robot_base_rotation, atol=5.0)

    # Turn right.
    robot_base_rotation = robot.data["rotations"][0].copy()
    robot.TurnRight(90, 1)
    bathing_env.step(num_steps_per_command)
    new_robot_base_rotation = robot.data["rotations"][0].copy()
    expected_robot_base_rotation = np.add(robot_base_rotation, (0.0, 90.0, 0))
    assert euler_angles_allclose(new_robot_base_rotation, expected_robot_base_rotation, atol=5.0)

def test_bathing_collision(bathing_env: BathingEnv):
    """
    Test for collision detection using GetCurrentCollisionPairs in the bathing env.
    """

    num_steps_per_command = 500
    robot = bathing_env.get_robot()

    # Drive against bed.
    robot.MoveBack(6, 0.5)

    bathing_env.step(num_steps_per_command)

    bathing_env.GetCurrentCollisionPairs()
    bathing_env.step()
    assert len(bathing_env.data["collision_pairs"]) > 0
    assert 221582 in bathing_env.data["collision_pairs"][0]
    assert 758554 in bathing_env.data["collision_pairs"][0]
    
    # Drive against drawer.
    robot.MoveForward(6, 0.5)

    bathing_env.step(num_steps_per_command)

    bathing_env.GetCurrentCollisionPairs()
    bathing_env.step()
    assert len(bathing_env.data["collision_pairs"]) > 0 
    assert 221582 in bathing_env.data["collision_pairs"][0]
    assert 758666 in bathing_env.data["collision_pairs"][0]

    # Drive away from drawer.
    robot.MoveBack(0.5, 0.5)

    bathing_env.step(num_steps_per_command)

    bathing_env.GetCurrentCollisionPairs()
    bathing_env.step()
    assert len(bathing_env.data["collision_pairs"]) == 0

def test_target_angle_drive(bathing_env: BathingEnv):
    """Tests for movement using `.TargetVelocity()` on the robot."""

    robot = bathing_env.get_robot()
    num_steps_per_command = 300

    # Drive forward by setting left and right velocities.
    robot_base_position = robot.data["positions"][0].copy()
    for _ in range(num_steps_per_command):
        robot.TargetVelocity(0.5, 0.5)
        bathing_env.step()

    new_robot_base_position = robot.data["positions"][0].copy()
    # Hits the drawer.
    expected_robot_base_position = np.add(robot_base_position, (0, 0, 0.51))
    assert np.allclose(new_robot_base_position, expected_robot_base_position, atol=0.03)

    # Drive backward by setting left and right velocities.
    robot_base_position = robot.data["positions"][0].copy()
    for _ in range(num_steps_per_command):
        robot.TargetVelocity(-0.5, -0.5)
        bathing_env.step()

    new_robot_base_position = robot.data["positions"][0].copy()
    # Hits the bed.
    expected_robot_base_position = np.add(robot_base_position, (0, 0, -1.08))
    assert np.allclose(new_robot_base_position, expected_robot_base_position, atol=0.1)

def test_target_angle_turn(bathing_env: BathingEnv):
    robot = bathing_env.get_robot()
    num_steps_per_command = 300

    # Drive left by setting left and right velocities.
    robot_base_rotation = robot.data["rotations"][0].copy()
    for _ in range(num_steps_per_command):
        robot.TargetVelocity(-0.25, 0.25)
        bathing_env.step()

    new_robot_base_rotation = robot.data["rotations"][0].copy()
    expected_robot_base_rotation = np.add(robot_base_rotation, (0, -40, 0))
    assert euler_angles_allclose(new_robot_base_rotation, expected_robot_base_rotation, atol=10.0)

    # Stop for a moment.
    robot.TargetVelocity(0, 0)
    bathing_env.step()

    # Drive right by setting left and right velocities.
    robot_base_rotation = robot.data["rotations"][0].copy()
    for _ in range(num_steps_per_command):
        robot.TargetVelocity(0.25, -0.25)
        bathing_env.step()

    new_robot_base_rotation = robot.data["rotations"][0].copy()
    expected_robot_base_rotation = np.add(robot_base_rotation, (0, 40, 0))
    assert euler_angles_allclose(new_robot_base_rotation, expected_robot_base_rotation, atol=10.0)
