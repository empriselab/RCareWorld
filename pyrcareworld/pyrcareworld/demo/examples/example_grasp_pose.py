print("""
This script demonstrates the visualization of grasp poses for a specified object within the RCareWorld environment using GraspSim.

What it Implements:
- Initializes the environment with the GraspSim object.
- Loads grasp pose data from a CSV file, including positions and quaternions.
- Visualizes the grasp poses on a specified 3D object using the SimpleFrankaGripper.

What the Functionality Covers:
- Understanding how to load and use pose data for grasp simulation in RCareWorld.
- Demonstrates the integration of external pose data with the environment's simulation capabilities.

Required Operations:
- Data Loading: Reads and processes pose data from a CSV file.
- Visualization: Displays the grasp poses on the object within the environment.
""")


import os
import sys
import pandas as pd

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import mesh_path
from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.graspsim_attr import GraspSimAttr

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Paths to object and pose data
obj_path = os.path.join(mesh_path, "drink1/drink1.obj")
pose_path = os.path.join(mesh_path, "drink1/grasps_rfu.csv")

# Read pose data from CSV
data = pd.read_csv(pose_path, usecols=["x", "y", "z", "qx", "qy", "qz", "qw"])
data = data.to_numpy()

# Extract positions and quaternions
positions = data[:, 0:3].reshape(-1).tolist()
quaternions = data[:, 3:7].reshape(-1).tolist()

# Initialize the environment
env = RCareWorld(executable_file=player_path)

# Create an instance of the GraspSim object
grasp_sim = env.InstanceObject(id=123123, name="GraspSim", attr_type=GraspSimAttr)

# Show grasp poses
grasp_sim.ShowGraspPose(
    mesh=os.path.abspath(obj_path),
    gripper="SimpleFrankaGripper",
    positions=positions,
    quaternions=quaternions,
)

# Close the environment
env.Pend()
env.Pend()
env.close()
