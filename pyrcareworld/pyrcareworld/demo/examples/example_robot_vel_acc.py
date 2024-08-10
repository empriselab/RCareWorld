print("""
This script demonstrates the control and movement of a Franka Panda robot in the RCareWorld environment, while calculating the acceleration of a linked mass point.

What it Implements:
- Initializes the environment with a Franka Panda robot and a MassPoint object.
- Moves and rotates the robot to an initial position and links a mass point to a specific joint of the robot.
- Calculates the acceleration of the mass point based on its velocity and performs random movements of the robot in a loop.

What the Functionality Covers:
- Understanding how to manipulate robotic arms using inverse kinematics (IK) in RCareWorld.
- Demonstrates linking objects to robot joints and calculating dynamic properties like acceleration.

Required Operations:
- Loop: Continuously calculates acceleration and performs random movements of the robot.
- Debugging: Enables debugging of object poses and performs simulation steps with detailed control.
""")

import os
import sys
import numpy as np
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with specified assets
env = RCareWorld(assets=["franka_panda"],executable_file=player_path)

# Enable debugging of object poses and set the time step
env.DebugObjectPose()
env.SetTimeStep(0.005)

# Create an instance of the Franka Panda robot and set its IK target offset
robot = env.InstanceObject(name="franka_panda", id=123456, attr_type=attr.ControllerAttr)
robot.SetIKTargetOffset(position=[0, 0.105, 0])
env.step()

# Move and rotate the robot to the initial position
robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0, speed_based=False)
robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
robot.WaitDo()

# Perform additional simulation steps
env.step(100)

# Create an instance of a MassPoint object
mass_point = env.InstanceObject(name="MassPoint", id=999, attr_type=attr.RigidbodyAttr)

# Get the world position of a specific joint and link the mass point to the robot
robot.GetJointWorldPointFromLocal(8, [0, 0, 0])
env.step(simulate=False)
mass_point.SetPosition(robot.data["result_joint_world_point"])
mass_point.Link(robot.id, 8)

# Initialize the last velocity variable
last_velocity = [0, 0, 0]

# Main loop to calculate acceleration and perform random movements
print("Stop printing acc for debugging")
while True:
    env.step()
    # Calculate acceleration
    acc = np.array(mass_point.data["velocity"]) - np.array(last_velocity) / env.data["fixed_delta_time"]
    # print("acc", np.linalg.norm(acc))
    last_velocity = mass_point.data["velocity"]

    # If the robot has finished its move, perform a random movement
    if robot.data["move_done"]:
        vector = np.random.rand(3)
        vector /= np.linalg.norm(vector)
        vector *= np.random.uniform(-0.1, 0.1)
        robot.IKTargetDoMove(position=vector.tolist(), duration=0.1, speed_based=True, relative=True)
