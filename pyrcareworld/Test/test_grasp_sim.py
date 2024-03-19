import os
import numpy as np

try:
    import pandas as pd
except ImportError:
    print("This feature requires pandas, please install with `pip install pandas`")
    raise
try:
    import open3d as o3d
except ImportError:
    print("This feature requires open3d, please install with `pip install open3d`")
    raise

from pyrcareworld.envs.rcareworld_env import RCareWorldBaseEnv


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


mesh_path = "../Mesh/drink1/drink1.obj"

points, normals = get_grasp_pose(mesh_path, 100)
points = points.reshape(-1).tolist()
normals = normals.reshape(-1).tolist()

env = RCareWorldBaseEnv(assets=["GraspSim"])
env.asset_channel.set_action("InstanceObject", id=123123, name="GraspSim")
# grasp sim
env.instance_channel.set_action(
    "StartGraspSim",
    id=123123,
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
# env.instance_channel.set_action(
#     'GenerateGraspPose',
#     id=123123,
#     mesh=os.path.abspath(mesh_path),
#     gripper='SimpleFrankaGripper',
#     points=points,
#     normals=normals,
#     depth_range_min=-0.05,
#     depth_range_max=0,
#     depth_lerp_count=5,
#     angle_lerp_count=5,
# )
env.step()
while not env.instance_channel.data[123123]["done"]:
    env.step()


points = env.instance_channel.data[123123]["points"]
points = np.array(points).reshape([-1, 3])
quaternions = env.instance_channel.data[123123]["quaternions"]
quaternions = np.array(quaternions).reshape([-1, 4])
width = env.instance_channel.data[123123]["width"]
width = np.array(width).reshape([-1, 1])
print(points.shape)
data = np.concatenate((points, quaternions, width), axis=1)
csv = pd.DataFrame(data, columns=["x", "y", "z", "qx", "qy", "qz", "qw", "width"])

csv_path = os.path.join(os.path.dirname(mesh_path), "grasps_rfu.csv")
csv.to_csv(csv_path, index=True, header=True)

while True:
    env.step()
