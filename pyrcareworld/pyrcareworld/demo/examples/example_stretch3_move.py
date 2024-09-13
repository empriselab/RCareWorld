print("""
This script demonstrates the control of a Stretch robot in the RCareWorld environment, including movement and gripper manipulation.

What it Implements:
- Initializes the environment with a Stretch robot and sets its initial properties, such as position and mobility.
- Performs a series of actions including opening the gripper, moving the robot using inverse kinematics (IK), and rotating the robot.
- =====***NOTE: This script does not include texture loading; the robot will appear white by default.***=====
- =====***To load textures, you must manually include texture files and modify the script accordingly.***=====

What the Functionality Covers:
- Understanding how to control a robot's movement and gripper operations in RCareWorld.
- Demonstrates basic robot movements, including forward, backward, and rotational commands.

Required Operations:
- Robot Control: Moves the robot and manipulates its gripper using IK commands.
- Optional Movements: Additional movement commands (e.g., turning, moving forward/backward) can be uncommented for further control.
""")


import time
import os
import sys
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with the specified asset
env = RCareWorld(assets=["stretch_3"], executable_file=player_path)
env.SetTimeStep(0.005)

print("Environment initialized.")

# Create an instance of the Stretch robot and set its initial properties
stretch = env.InstanceObject(name="stretch-3", id=221582, attr_type=attr.ControllerAttr)

stretch.SetPosition([0, 0, 0])
stretch.SetImmovable(False)
env.step()

print("Stretch robot created.")

time.sleep(10)

gripper = env.GetAttr(2215820)
gripper.GripperOpen()
env.step()

stretch.IKTargetDoMove(position=[0, 0.5, 0.5], duration=3, speed_based=False)
# stretch.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
stretch.WaitDo()

# Uncomment the following block to move and turn the Stretch robot with specific steps
# stretch.MoveForward(1, 0.2)
# env.step(300)
# stretch.TurnLeft(90, 60)
# env.step(300)
# stretch.MoveForward(1, 0.2)
# env.step(300)
# stretch.TurnLeft(90, 30)
# env.step(300)
# stretch.MoveForward(1, 0.2)
# env.step(300)
# stretch.TurnRight(90, 30)
# env.step(300)
# stretch.MoveBack(1, 0.2)
# env.step(300)
# stretch.TurnRight(90, 30)
# env.step(300)

stretch.TurnLeft(90, 30)
env.step(300)
