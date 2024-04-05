from pyrcareworld.envs.rcareworld_env import RCareWorldBaseEnv
import pyrcareworld.utils.depth_processor as dp
import numpy as np

try:
    import open3d as o3d
except ImportError:
    print("This feature requires open3d, please install with `pip install open3d`")
    raise

env = RCareWorldBaseEnv(scene_file="PointCloud.json")
env.instance_channel.set_action(
    "GetDepthEXR",
    id=698548,
    width=1920,
    height=1080,
)
env.instance_channel.set_action("GetRGB", id=698548, width=1920, height=1080)
env.instance_channel.set_action("GetID", id=698548, width=1920, height=1080)
env._step()

image_rgb = env.instance_channel.data[698548]["rgb"]
image_depth_exr = env.instance_channel.data[698548]["depth_exr"]
fov = env.instance_channel.data[698548]["fov"]
local_to_world_matrix = env.instance_channel.data[698548]["local_to_world_matrix"]
local_to_world_matrix = np.reshape(local_to_world_matrix, [4, 4]).T
point1 = dp.image_bytes_to_point_cloud(
    image_rgb, image_depth_exr, fov, local_to_world_matrix
)

env.instance_channel.set_action(
    "GetDepthEXR",
    id=698550,
    width=1920,
    height=1080,
)
env.instance_channel.set_action("GetRGB", id=698550, width=1920, height=1080)
env.instance_channel.set_action("GetID", id=698550, width=1920, height=1080)
env._step()
image_rgb = env.instance_channel.data[698550]["rgb"]
image_depth_exr = env.instance_channel.data[698550]["depth_exr"]
fov = env.instance_channel.data[698550]["fov"]
local_to_world_matrix = env.instance_channel.data[698550]["local_to_world_matrix"]
local_to_world_matrix = np.reshape(local_to_world_matrix, [4, 4]).T
point2 = dp.image_bytes_to_point_cloud(
    image_rgb, image_depth_exr, fov, local_to_world_matrix
)
env.close()

# env2 = RCareWorldBaseEnv()
# env2.asset_channel.set_action(
#     "InstanceObject",
#     name='PointCloud',
#     id=123456
# )
# env2.instance_channel.set_action(
#     "ShowPointCloud",
#     id=123456,
#     positions=np.array(point2.points).reshape(-1).tolist(),
#     colors=np.array(point2.colors).reshape(-1).tolist(),
# )
# while 1:
#     env2._step()

# unity space to open3d space and show
point1.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point2.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
coorninate = o3d.geometry.TriangleMesh.create_coordinate_frame()
o3d.visualization.draw_geometries([point1, point2, coorninate])
