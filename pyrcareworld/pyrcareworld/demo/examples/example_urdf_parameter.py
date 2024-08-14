print("""
This script demonstrates the loading and configuration of a Franka Panda robot URDF model in the RCareWorld environment.

What it Implements:
- Initializes the environment and loads the Franka Panda robot URDF model with the Z-axis as the specified axis.
- Sets the initial transform of the robot and disables its native inverse kinematics (IK).
- Displays the articulation parameters for the robot, allowing for joint control and inspection.

What the Functionality Covers:
- Understanding how to load and configure URDF models in RCareWorld.
- Demonstrates how to disable native IK and inspect articulation parameters for fine-grained control.

Required Operations:
- Configuration: Sets the robot's transform and disables native IK for custom control.
- Parameter Inspection: Displays articulation parameters for detailed inspection and manipulation.
""")

import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.demo import urdf_path
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment
env = RCareWorld(executable_file=player_path)

# Load the Franka Panda robot URDF with the specified axis
robot = env.LoadURDF(path=os.path.join(urdf_path, "Franka/panda.urdf"), axis="z")

# Set the initial transform of the robot
robot.SetTransform(position=[0, 0, 0])

# Disable native IK for the robot
robot.EnabledNativeIK(False)

# Show the articulation parameters for the robot
env.ShowArticulationParameter(robot.id)

# End the environment session
env.Pend()
