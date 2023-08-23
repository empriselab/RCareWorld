import cv2
import numpy as np

try:
    import open3d as o3d
except ImportError:
    print("This feature requires open3d, please install with `pip install open3d`")
    raise
import pyrcareworld.utils.utility as utility
import pyrcareworld.utils.depth_processor as dp
from pyrcareworld.envs.base_env import RCareWorldBaseEnv

env = RCareWorldBaseEnv(scene_file="ActiveDepth.json")

main_intrinsic_matrix = [600, 0, 0, 0, 600, 0, 240, 240, 1]
ir_intrinsic_matrix = [480, 0, 0, 0, 480, 0, 240, 240, 1]

nd_main_intrinsic_matrix = np.reshape(main_intrinsic_matrix, [3, 3]).T

env.instance_channel.set_action(
    "GetRGB", id=789789, intrinsic_matrix=main_intrinsic_matrix
)
env._step()
image_byte = env.instance_channel.data[789789]["rgb"]
image_rgb = np.frombuffer(image_byte, dtype=np.uint8)
image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
# cv2.imshow("show", image_rgb)
# cv2.waitKey(0)
image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
image_rgb = np.transpose(image_rgb, [1, 0, 2])

env.instance_channel.set_action(
    "GetID", id=789789, intrinsic_matrix=main_intrinsic_matrix
)
env._step()
image_id = env.instance_channel.data[789789]["id_map"]
image_id = np.frombuffer(image_id, dtype=np.uint8)
image_id = cv2.imdecode(image_id, cv2.IMREAD_COLOR)
# cv2.imshow("show", image_id)
# cv2.waitKey(0)
image_id = cv2.cvtColor(image_id, cv2.COLOR_BGR2RGB)
# image_id = np.transpose(image_id, [1, 0, 2])

env.instance_channel.set_action(
    "GetDepthEXR",
    id=789789,
    intrinsic_matrix=main_intrinsic_matrix,
)
env._step()
image_depth_exr = env.instance_channel.data[789789]["depth_exr"]

env.instance_channel.set_action(
    "GetActiveDepth",
    id=789789,
    main_intrinsic_matrix=main_intrinsic_matrix,
    ir_intrinsic_matrix=ir_intrinsic_matrix,
)
env._step()
image_active_depth = env.instance_channel.data[789789]["active_depth"]
image_active_depth = np.transpose(image_active_depth, [1, 0])

local_to_world_matrix = env.instance_channel.data[789789]["local_to_world_matrix"]
local_to_world_matrix = np.reshape(local_to_world_matrix, [4, 4]).T

# point = dp.image_array_to_point_cloud(image_rgb, image_active_depth, 45, local_to_world_matrix)

color = utility.EncodeIDAsColor(568451)[0:3]
point11 = dp.image_bytes_to_point_cloud_intrinsic_matrix(
    image_byte, image_depth_exr, nd_main_intrinsic_matrix, local_to_world_matrix
)
point11 = dp.mask_point_cloud_with_id_color(point11, image_id, color)
point1 = dp.image_array_to_point_cloud_intrinsic_matrix(
    image_rgb, image_active_depth, nd_main_intrinsic_matrix, local_to_world_matrix
)
point1 = dp.mask_point_cloud_with_id_color(point1, image_id, color)
point10 = dp.filter_active_depth_point_cloud_with_exact_depth_point_cloud(
    point1, point11
)

##################################################

env.instance_channel.set_action(
    "GetRGB", id=123123, intrinsic_matrix=main_intrinsic_matrix
)
env._step()
image_byte = env.instance_channel.data[123123]["rgb"]
image_rgb = np.frombuffer(image_byte, dtype=np.uint8)
image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
# cv2.imshow("show", image_rgb)
# cv2.waitKey(0)
image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
image_rgb = np.transpose(image_rgb, [1, 0, 2])

env.instance_channel.set_action(
    "GetID", id=123123, intrinsic_matrix=main_intrinsic_matrix
)
env._step()
image_id = env.instance_channel.data[123123]["id_map"]
image_id = np.frombuffer(image_id, dtype=np.uint8)
image_id = cv2.imdecode(image_id, cv2.IMREAD_COLOR)
# cv2.imshow("show", image_id)
# cv2.waitKey(0)
image_id = cv2.cvtColor(image_id, cv2.COLOR_BGR2RGB)
# image_id = np.transpose(image_id, [1, 0, 2])

env.instance_channel.set_action(
    "GetDepthEXR",
    id=123123,
    intrinsic_matrix=main_intrinsic_matrix,
)
env._step()
image_depth_exr = env.instance_channel.data[123123]["depth_exr"]


env.instance_channel.set_action(
    "GetActiveDepth",
    id=123123,
    main_intrinsic_matrix=main_intrinsic_matrix,
    ir_intrinsic_matrix=ir_intrinsic_matrix,
)
env._step()
image_active_depth = env.instance_channel.data[123123]["active_depth"]
image_active_depth = np.transpose(image_active_depth, [1, 0])

local_to_world_matrix = env.instance_channel.data[123123]["local_to_world_matrix"]
local_to_world_matrix = np.reshape(local_to_world_matrix, [4, 4]).T
env.close()

# point = dp.image_array_to_point_cloud(image_rgb, image_active_depth, 45, local_to_world_matrix)
point22 = dp.image_bytes_to_point_cloud_intrinsic_matrix(
    image_byte, image_depth_exr, nd_main_intrinsic_matrix, local_to_world_matrix
)
point22 = dp.mask_point_cloud_with_id_color(point22, image_id, color)
point2 = dp.image_array_to_point_cloud_intrinsic_matrix(
    image_rgb, image_active_depth, nd_main_intrinsic_matrix, local_to_world_matrix
)
point2 = dp.mask_point_cloud_with_id_color(point2, image_id, color)
point20 = dp.filter_active_depth_point_cloud_with_exact_depth_point_cloud(
    point2, point22
)

# unity space to open3d space and show
point11.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point22.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point1.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point2.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point10.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point20.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
coorninate = o3d.geometry.TriangleMesh.create_coordinate_frame()

o3d.visualization.draw_geometries([point11, point22, coorninate])
o3d.visualization.draw_geometries([point1, point2, coorninate])
o3d.visualization.draw_geometries([point10, point20, coorninate])

env2 = RCareWorldBaseEnv(
    executable_file="@Editor",
)
env2.asset_channel.set_action("InstanceObject", name="PointCloud", id=123456)
env2.instance_channel.set_action(
    "ShowPointCloud",
    id=123456,
    positions=np.array(point2.points).reshape(-1).tolist(),
    colors=np.array(point2.colors).reshape(-1).tolist(),
)
while 1:
    env2._step()
