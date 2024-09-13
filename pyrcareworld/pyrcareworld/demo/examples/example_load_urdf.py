print("""
This script demonstrates loading multiple URDF models of robots and performing inverse kinematics (IK) movements with the UR5 robot in the RCareWorld environment.

What it Implements:
- Initializes the environment and loads URDF models for the UR5, Yumi, and Kinova robots. Note that the URDF loader does not render the texture, so while the robot structures and joints are correctly loaded, the visual appearances may lack textures.
- Performs a series of IK movements with the UR5 robot to demonstrate its control capabilities.

What the Functionality Covers:
- Understanding how to load and manipulate multiple URDF models in the RCareWorld environment.
- Demonstrates how to execute IK movements, including translations and rotations, on the UR5 robot.

Required Operations:
- Sequential IK Movements: The script performs a series of movements with the UR5 robot and waits for each to complete before proceeding.
""")

import os
import sys
import time

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.utils.rfuniverse_utility as utility
from pyrcareworld.demo import urdf_path
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment
env = RCareWorld(executable_file=player_path)

# Load the UR5 robot with native IK enabled
ur5 = env.LoadURDF(path=os.path.join(urdf_path, "UR5/ur5_robot.urdf"), native_ik=True)
ur5.SetTransform(position=[1, 0, 0])

# Load the Yumi robot with native IK disabled
yumi = env.LoadURDF(path=os.path.join(urdf_path, "yumi_description/urdf/yumi.urdf"), native_ik=False)
yumi.SetTransform(position=[2, 0, 0])

# Load the Kinova robot with native IK disabled
kinova = env.LoadURDF(path=os.path.join(urdf_path, "kinova_gen3/GEN3_URDF_V12.urdf"), native_ik=False)
kinova.SetTransform(position=[3, 0, 0])

# Perform an initial simulation step to update the environment
env.step()

# Perform a series of IK movements with the UR5 robot
ur5.IKTargetDoMove(position=[0, 0.5, 0], duration=0.1, relative=True)
ur5.WaitDo()

ur5.IKTargetDoMove(position=[0, 0, -0.5], duration=0.1, relative=True)
ur5.WaitDo()

ur5.IKTargetDoMove(position=[0, -0.2, 0.3], duration=0.1, relative=True)
ur5.IKTargetDoRotateQuaternion(
    quaternion=utility.UnityEulerToQuaternion([0, 90, 0]), duration=30, relative=True
)
ur5.WaitDo()

# End the environment session
time.sleep(30)
env.Pend()
