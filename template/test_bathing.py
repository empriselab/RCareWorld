import json
from pyrcareworld.envs.base_env import RCareWorld
import numpy as np
import cv2
env = RCareWorld(executable_file="Player/Player.x86_64")

stretch_id = 221582
robot = env.GetAttr(stretch_id)
env.step()

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(2215820)
gripper.GripperOpen()
env.step(300)


# gripper.GripperClose()
# env.step()



# sponge = env.GetAttr(91846)
# env.step()
# print(sponge.data)

camera_hand = env.GetAttr(654321)
camera_hand.SetTransform(position=gripper.data['position'], rotation=[0, 0, 0])
camera_hand.SetParent(2215820)
camera_hand.GetRGB(512, 512)
env.step()
rgb = np.frombuffer(camera_hand.data["rgb"], dtype=np.uint8)
rgb = cv2.imdecode(rgb, cv2.IMREAD_COLOR)
cv2.imwrite("rgb_head.png", rgb)

# Main loop to create, move, and manipulate boxes
while True:


    # Random positions
    position1 = (-0.657, 0.941, 1.645)
    position2 = (-0.263, 1.063, 1.645)

    # Move the robot to the first box, pick it up, and move it to the second box's position
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
    # print(sponge.GetRealTimeForces())

    env.step()
