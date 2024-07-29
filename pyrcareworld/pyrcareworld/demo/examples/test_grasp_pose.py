import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from demo import mesh_path
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.graspsim_attr import GraspSimAttr
try:
    import pandas as pd
except ImportError:
    print("This feature requires pandas, please install with `pip install pandas`")
    raise


def test_grasp_pose():
    """Tests loading and visualizing saved grasp poses."""
    mesh_path = os.path.join('/home/cathy/Workspace/rcareworld_new/pyrcareworld/test/pyrcareworld_test/mesh/', "drink1/drink1.obj")
    pose_path = os.path.join("/home/cathy/Workspace/rcareworld_new/pyrcareworld/test/pyrcareworld_test/mesh/", "drink1/grasps_rfu.csv")

    data = pd.read_csv(pose_path, usecols=["x", "y", "z", "qx", "qy", "qz", "qw"])
    data = data.to_numpy()
    positions = data[:, 0:3].reshape(-1).tolist()
    quaternions = data[:, 3:7].reshape(-1).tolist()

    env = RCareWorld()
    grasp_sim = env.InstanceObject(id=123123, name="GraspSim", attr_type=GraspSimAttr)
    grasp_sim.ShowGraspPose(
        mesh=os.path.abspath(mesh_path),
        gripper="SimpleFrankaGripper",
        positions=positions,
        quaternions=quaternions,
    )

    env.close()
