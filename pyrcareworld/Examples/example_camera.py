from pyrcareworld.envs import RCareWorld
import numpy as np
import pyrcareworld.utils.depth_processor as dp
import open3d as o3d
import cv2

env = RCareWorld(scene_file="ActiveDepth.json")
main_intrinsic_matrix = [600, 0, 0, 0, 600, 0, 240, 240, 1]
ir_intrinsic_matrix = [480, 0, 0, 0, 480, 0, 240, 240, 1]
camera = env.create_camera(
    id=789789, name="camera", intrinsic_matrix=main_intrinsic_matrix
)

nd_main_intrinsic_matrix = np.reshape(main_intrinsic_matrix, [3, 3]).T
camera.initializeRGB()
img_rgb = camera.getRGB()
cv2.imshow("show", img_rgb)
cv2.waitKey(0)

camera.initializeDepthEXR()
img_depth_exr = camera.getDepthEXR()
camera.initializeActiveDepthWithIntrinsic(ir_intrinsic_matrix)
img_active_depth = camera.getActiveDepth()
local_to_world_matrix = camera.getLocalToWorldMatrix()

point2 = dp.image_array_to_point_cloud_intrinsic_matrix(
    img_rgb, img_active_depth, nd_main_intrinsic_matrix, local_to_world_matrix
)

# unity space to open3d space and show
point2.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
print(point2)
coorninate = o3d.geometry.TriangleMesh.create_coordinate_frame()
o3d.visualization.draw_geometries([point2, coorninate])
# env.close()

# env2 = RCareWorld(executable_file='@Editor',)
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

for i in range(500000):
    env._step()
