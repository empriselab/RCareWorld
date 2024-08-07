import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.demo import urdf_path
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "C:\\Users\\15156\\Desktop\\New folder (2)\\RCareWorld.exe")

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
