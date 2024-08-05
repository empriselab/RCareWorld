"""
An example of the usage of the bathing environment.

The sponge will be attached to the robot's hand if the grasp center and the ponge are close enough. (distancd < 0.1m)
The sponge will be detached from the robot's hand if you call the GripperOpen() function.

You can obtain low level information of the sponge, the robot, and use unlimited numbers of cameras to observe the scene.

The threshold for a comfortable force on the human body is set to 1-6N.

"""

import json
from pyrcareworld.envs.base_env import RCareWorld
import numpy as np
import cv2

# Initialize the environment with the specified executable file
env = RCareWorld()

stretch_id = 221582
robot = env.GetAttr(stretch_id)
env.step()

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(2215820)
gripper.GripperOpen()
env.step(300)

gripper.GripperClose()
env.step()



sponge = env.GetAttr(91846)
env.step()
print(sponge.data)

camera_hand = env.GetAttr(654321)
camera_hand.SetTransform(position=gripper.data['position'], rotation=[0, 0, 0])
camera_hand.SetParent(2215820)
camera_hand.GetRGB(512, 512)
env.step()
rgb = np.frombuffer(camera_hand.data["rgb"], dtype=np.uint8)
rgb = cv2.imdecode(rgb, cv2.IMREAD_COLOR)
cv2.imwrite("rgb_hand.png", rgb)

# Random positions
position1 = (-0.657, 0.941, 1.645)
position2 = (-0.263, 1.063, 1.645)

robot.IKTargetDoMove(
    position=[position1[0], position1[1] + 0.5, position1[2]],
    duration=2,
    speed_based=False,
)
robot.WaitDo()
robot.IKTargetDoMove(
    position=[position1[0], position1[1], position1[2]],
    duration=2,
    speed_based=False,
)
robot.WaitDo()
gripper.GripperClose()
env.step(50)
robot.IKTargetDoMove(
    position=[0, 0.5, 0], duration=2, speed_based=False, relative=True
)
robot.WaitDo()
robot.IKTargetDoMove(
    position=[position2[0], position2[1] + 0.5, position2[2]],
    duration=4,
    speed_based=False,
)
robot.WaitDo()
robot.IKTargetDoMove(
    position=[position2[0], position2[1] + 0.06, position2[2]],
    duration=2,
    speed_based=False,
)

    

# print(sponge.GetPaintProportion())
# print(sponge.GetEffectiveForceProportion())
print(sponge.GetForce())

env.step()
