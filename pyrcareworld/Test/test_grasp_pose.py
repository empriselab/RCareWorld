import os

try:
    import pandas as pd
except ImportError:
    print("This feature requires pandas, please install with `pip install pandas`")
    raise
from pyrcareworld.envs.rcareworld_env import RCareWorldBaseEnv

mesh_path = "../Mesh/drink1/drink1.obj"
pose_path = "../Mesh/drink1/grasps_rfu.csv"

data = pd.read_csv(pose_path, usecols=["x", "y", "z", "qx", "qy", "qz", "qw"])
data = data.to_numpy()
positions = data[:, 0:3].reshape(-1).tolist()
quaternions = data[:, 3:7].reshape(-1).tolist()

env = RCareWorldBaseEnv()

env.asset_channel.set_action("InstanceObject", id=123123, name="GraspSim")
env.instance_channel.set_action(
    "ShowGraspPose",
    id=123123,
    mesh=os.path.abspath(mesh_path),
    gripper="SimpleFrankaGripper",
    positions=positions,
    quaternions=quaternions,
)
while True:
    env._step()
