import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.attributes.graspsim_attr import GraspSimAttr
from pyrcareworld.envs.base_env import RCareWorld
import numpy as np
try:
    import pandas as pd
except ImportError:
    raise Exception(
        "This feature requires pandas, please install with `pip install pandas`"
    )
try:
    import open3d as o3d
except ImportError:
    raise Exception(
        "This feature requires open3d, please install with `pip install open3d`"
    )


def get_grasp_pose(file: str, points_count, scale: float = 1):
    mesh = o3d.io.read_triangle_mesh(file)
    mesh.scale(scale, np.array([0, 0, 0]))
    sample_points = mesh.sample_points_poisson_disk(
        points_count, use_triangle_normal=True
    )
    sample_points.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    points = np.asarray(sample_points.points)
    normals = np.asarray(sample_points.normals)
    return points, normals


def test_grasp_sim():
    """Tests simulating sampled grasps."""
    mesh_path = os.path.join("/home/cathy/Workspace/rcareworld_new/pyrcareworld/test/pyrcareworld_test/mesh/","drink1/drink1.obj")

    points, normals = get_grasp_pose(mesh_path, 100)
    points = points.reshape(-1).tolist()
    normals = normals.reshape(-1).tolist()

    env = RCareWorld(assets=["GraspSim"])
    grasp_sim = env.InstanceObject(id=123123, name="GraspSim", attr_type=GraspSimAttr)
    grasp_sim.StartGraspSim(
        mesh=os.path.abspath(mesh_path),
        gripper="franka_hand",
        points=points,
        normals=normals,
        depth_range_min=-0.05,
        depth_range_max=0,
        depth_lerp_count=5,
        angle_lerp_count=5,
        parallel_count=100,
    )

    # only show grasp pose
    # grasp_sim.GenerateGraspPose(mesh=os.path.abspath(mesh_path),
    #                             gripper='SimpleFrankaGripper',
    #                             points=points,
    #                             normals=normals,
    #                             depth_range_min=-0.05,
    #                             depth_range_max=0,
    #                             depth_lerp_count=5,
    #                             angle_lerp_count=5,
    #                             )
    env.step()
    while not grasp_sim.data['done']:
        env.step()

    points = grasp_sim.data["points"]
    points = np.array(points).reshape([-1, 3])
    quaternions = grasp_sim.data["quaternions"]
    quaternions = np.array(quaternions).reshape([-1, 4])
    width = grasp_sim.data["width"]
    width = np.array(width).reshape([-1, 1])

    env.close()

    data = np.concatenate((points, quaternions, width), axis=1)
    csv = pd.DataFrame(data, columns=["x", "y", "z", "qx", "qy", "qz", "qw", "width"])

    csv_path = os.path.join(os.path.dirname(mesh_path), "grasps_rfu.csv")
    csv.to_csv(csv_path, index=True, header=True)

    env.close()
