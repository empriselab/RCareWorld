import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
from demo import urdf_path

# Initialize the environment
env = RCareWorld()

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
