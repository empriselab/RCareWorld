print("""
This script demonstrates loading and interacting with a URDF model of a robot in the RCareWorld environment.

What it Implements:
- Initializes the environment and loads a URDF model of the UR5 robot. Note that the URDF loader does not render the texture, so while the robot's structure and joints are correctly loaded, the visual appearance may lack textures.
- Sets the initial transform for the robot and adjusts the camera view to focus on it.
- Displays the articulation parameters for the robot, allowing joint control via sliders.

What the Functionality Covers:
- Understanding how to load and manipulate URDF models in the RCareWorld environment.
- Demonstrates how to interact with robot joints through the articulation parameter sliders.

Required Operations:
- User Interaction: Allows the user to drag sliders to control each joint of the robot.
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

# Load a URDF model of the robot
robot = env.LoadURDF(
    path=os.path.join(urdf_path, "UR5/ur5_robot.urdf"),
    native_ik=False,
)

# Set the initial transform of the robot
robot.SetTransform(position=[0, 0, 0])
env.step()

# Set the view transform for the environment
env.SetViewTransform(position=[0, 1, 1])

# Print the robot's data for debugging
# print(robot.data)
print("Stop printing robot data for debugging.")

# Adjust the view to look at the robot's position
env.ViewLookAt(robot.data["position"])

# Show the articulation parameters for the robot, allowing joint control via sliders
env.ShowArticulationParameter(robot.id)

# Instructions for the user
print("You can then drag the sliders to control each joint of the robot.")

# End the environment session
env.Pend()
