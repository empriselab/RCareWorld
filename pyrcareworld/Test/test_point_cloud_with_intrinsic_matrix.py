from pyrcareworld.envs.rcareworld_env import RCareWorldBaseEnv
import pyrcareworld.utils.depth_processor as dp
import numpy as np

try:
    import open3d as o3d
except ImportError:
    print("This feature requires open3d, please install with `pip install open3d`")
    raise

env = RCareWorldBaseEnv(scene_file="PointCloud.json")

intrinsic_matrix = [960, 0, 0, 0, 960, 0, 960, 540, 1]
nd_intrinsic_matrix = np.reshape(intrinsic_matrix, [3, 3]).T

env.instance_channel.set_action(
    "GetDepthEXR", id=698548, intrinsic_matrix=intrinsic_matrix
)
env.instance_channel.set_action("GetRGB", id=698548, intrinsic_matrix=intrinsic_matrix)
env.instance_channel.set_action("GetID", id=698548, intrinsic_matrix=intrinsic_matrix)
env._step()

image_rgb = env.instance_channel.data[698548]["rgb"]
image_depth_exr = env.instance_channel.data[698548]["depth_exr"]
local_to_world_matrix = env.instance_channel.data[698548]["local_to_world_matrix"]
local_to_world_matrix = np.reshape(local_to_world_matrix, [4, 4]).T
point1 = dp.image_bytes_to_point_cloud_intrinsic_matrix(
    image_rgb, image_depth_exr, nd_intrinsic_matrix, local_to_world_matrix
)

env.instance_channel.set_action(
    "GetDepthEXR", id=698550, intrinsic_matrix=intrinsic_matrix
)
env.instance_channel.set_action("GetRGB", id=698550, intrinsic_matrix=intrinsic_matrix)
env.instance_channel.set_action("GetID", id=698550, intrinsic_matrix=intrinsic_matrix)
env._step()
image_rgb = env.instance_channel.data[698550]["rgb"]
image_depth_exr = env.instance_channel.data[698550]["depth_exr"]
local_to_world_matrix = env.instance_channel.data[698550]["local_to_world_matrix"]
local_to_world_matrix = np.reshape(local_to_world_matrix, [4, 4]).T
point2 = dp.image_bytes_to_point_cloud_intrinsic_matrix(
    image_rgb, image_depth_exr, nd_intrinsic_matrix, local_to_world_matrix
)
env.close()

# unity space to open3d space and show
point1.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point2.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
coorninate = o3d.geometry.TriangleMesh.create_coordinate_frame()
o3d.visualization.draw_geometries([point1, point2, coorninate])
