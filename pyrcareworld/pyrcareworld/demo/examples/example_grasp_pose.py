import os
import sys
import pandas as pd

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import mesh_path
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.graspsim_attr import GraspSimAttr

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
env = RCareWorld()

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
env.close()
