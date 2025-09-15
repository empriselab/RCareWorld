import os
import sys
import random
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld


env = RCareWorld()

# Create an instance of the Franka Panda robot and set its IK target offset
robot = env.GetAttr(315893)

# robot.SetIKTargetOffset(position=[0, 0.105, 0])
env.step(200)

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(3158930)
gripper.GripperOpen()

initialize_target = env.GetAttr(5678)
env.step()
initialize_position = initialize_target.data["position"]

robot.IKTargetDoMove(
        position=initialize_position,
        duration=0,
        speed_based=False,
    )
robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)

shoulder_id = 3001
elbow_id = 3002
wrist_id = 3003

pad_dry_wp_id = 3004

shoulder = env.GetAttr(shoulder_id)
elbow = env.GetAttr(elbow_id)
wrist = env.GetAttr(wrist_id)
pad_dry_wp = env.GetAttr(pad_dry_wp_id)

shoulder_position = shoulder.data["position"]
elbow_position = elbow.data["position"]
wrist_position = wrist.data["position"]
pad_dry_wp_position = pad_dry_wp.data["position"]
env.step()

# move to shoulder
robot.IKTargetDoMove(
        position=[shoulder_position[0], shoulder_position[1]+0.1, shoulder_position[2]],
        duration=3,
        speed_based=False,
    )

for i in range(150):
    env.step()

# hop to wp
# hop up
up_hopping_point_1 = [0.5*(shoulder_position[0]+pad_dry_wp_position[0]),
                      0.5*(shoulder_position[1]+pad_dry_wp_position[1])+0.2,
                      0.5*(shoulder_position[2]+pad_dry_wp_position[2])]
robot.IKTargetDoMove(
        position=up_hopping_point_1,
        duration=3,
        speed_based=False,
    )

for i in range(150):
    env.step()

# hop down
robot.IKTargetDoMove(
        position=pad_dry_wp_position,
        duration=3,
        speed_based=False,
    )
for i in range(150):
    env.step()

# hop up again
up_hopping_point_2 = [0.5*(elbow_position[0]+pad_dry_wp_position[0]),
                      0.5*(elbow_position[1]+pad_dry_wp_position[1])+0.2,
                      0.5*(elbow_position[2]+pad_dry_wp_position[2])]
robot.IKTargetDoMove(
        position=up_hopping_point_2,
        duration=3,
        speed_based=False,
    )
for i in range(150):
    env.step()

robot.IKTargetDoMove(
        position=[elbow_position[0], elbow_position[1]+0.1, elbow_position[2]],
        duration=3,
        speed_based=False,
    )
for i in range(150):
    env.step()
# 150 steps for 3 seconds (3/0.02)
for i in range(150):
    env.step()




env.Pend()





