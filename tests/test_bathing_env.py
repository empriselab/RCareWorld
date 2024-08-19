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

    # Extract the relevant objects.
    robot = bathing_env.get_robot()
    gripper = bathing_env.get_gripper()
    camera = bathing_env.get_camera()
    sponge = bathing_env.get_sponge()

    # Attach the camera to the robot's gripper.
    camera.SetTransform(position=gripper.data['position'], rotation=[0, 0, 0])
    camera.SetParent(gripper.id)

    # Move the gripper up so that the sponge can be seen.
    robot.IKTargetDoMove(
        position=[-0.6, 0.75, 1.25],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()

    # Test getting an RGB image.
    img_size = 512
    camera.GetRGB(img_size, img_size)
    bathing_env.step()
    rgb = np.frombuffer(camera.data["rgb"], dtype=np.uint8)
    rgb = cv2.imdecode(rgb, cv2.IMREAD_COLOR)
    assert rgb.shape == (img_size, img_size, 3)
    
    # The sponge should be in view.
    # TODO https://github.com/empriselab/RCareWorld/discussions/103
    # camera.Get2DBBox()
    # bathing_env.step()
    # bboxes2d = camera.data["2d_bounding_box"]
    # assert sponge.id in bboxes2d
    # bboxes3d = camera.Get3DBBox()
    # bathing_env.step()
    # bboxes3d = camera.data["3d_bounding_box"]
    # assert sponge.id in bboxes3d

    # Test GetAmodalMask() for the sponge.
    camera.GetAmodalMask(sponge.id, img_size, img_size)
    bathing_env.step()
    amodal_mask = np.frombuffer(camera.data["amodal_mask"], dtype=np.uint8)
    amodal_mask = cv2.imdecode(amodal_mask, cv2.IMREAD_COLOR)
    import ipdb; ipdb.set_trace()



# def test_snippet():


#     from pyrcareworld.envs.bathing_env import BathingEnv

#     import pytest
#     import cv2
#     import numpy as np

#     env = BathingEnv(graphics=True)

#     robot = env.GetAttr(221582)
#     gripper = env.GetAttr(2215820)
#     sponge = env.GetAttr(91846)
#     camera_hand = env.GetAttr(654321)
#     camera_hand.SetTransform(position=gripper.data['position'], rotation=[0, 0, 0])
#     camera_hand.SetParent(2215820)
#     env.step()

#     # Move the gripper up so that the sponge can be seen.
#     robot.IKTargetDoMove(
#         position=[-0.6, 0.75, 1.25],
#         duration=2,
#         speed_based=False,
#     )
#     robot.WaitDo()
#     env.step()

#     camera_hand.GetRGB(512, 512)
#     env.step()
#     rgb = np.frombuffer(camera_hand.data["rgb"], dtype=np.uint8)
#     rgb = cv2.imdecode(rgb, cv2.IMREAD_COLOR)
#     cv2.imwrite("rgb_hand.png", rgb)

#     # The sponge should be in view.
#     env.step()
#     camera_hand.Get2DBBox()
#     env.step()
#     bboxes2d = camera_hand.data["2d_bounding_box"]
#     assert sponge.id in bboxes2d
