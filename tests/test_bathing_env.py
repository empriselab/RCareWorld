"""Tests for the bathing environment."""

from pyrcareworld.envs.bathing_env import BathingEnv

import pytest
import cv2
import numpy as np


@pytest.fixture(scope="session", name="bathing_env", autouse=True)
def _bathing_env_fixture():
    """Create a BathingEnv once and share it across tests."""
    env = BathingEnv(graphics=False)    
    yield env
    env.close()


def test_bathing_env_camera(bathing_env):
    """Tests for the camera in the bathing environment."""

    # Attach the camera to the robot's gripper.
    gripper = bathing_env.get_gripper()
    camera_hand = bathing_env.get_camera()
    camera_hand.SetTransform(position=gripper.data['position'], rotation=[0, 0, 0])
    camera_hand.SetParent(camera_hand.id)

    # Test getting an RGB image.
    camera_hand.GetRGB(16, 16)
    bathing_env.step()
    rgb = np.frombuffer(camera_hand.data["rgb"], dtype=np.uint8)
    rgb = cv2.imdecode(rgb, cv2.IMREAD_COLOR)
    assert rgb.shape == (16, 16, 3)
