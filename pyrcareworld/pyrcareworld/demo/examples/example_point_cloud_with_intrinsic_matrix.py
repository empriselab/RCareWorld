import os
import numpy as np
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.utils.depth_processor as dp

# Set environment variable for OpenCV EXR support
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

# Ensure open3d is installed
try:
    import open3d as o3d
except ImportError:
    raise Exception(
        "This feature requires open3d, please install with `pip install open3d`"
    )

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "Player/Player.x86_64")

# Initialize the environment with the specified scene file
env = RCareWorld(scene_file="PointCloud.json", executable_file=player_path)

# Define the intrinsic matrix
nd_intrinsic_matrix = np.array([[960, 0, 960], [0, 960, 540], [0, 0, 1]])

# Capture data from the first camera
camera1 = env.GetAttr(698548)
camera1.GetDepthEXR(intrinsic_matrix=nd_intrinsic_matrix)
camera1.GetRGB(intrinsic_matrix=nd_intrinsic_matrix)
camera1.GetID(intrinsic_matrix=nd_intrinsic_matrix)
env.step()

# Process the captured data from the first camera
image_rgb = camera1.data["rgb"]
image_depth_exr = camera1.data["depth_exr"]
local_to_world_matrix = camera1.data["local_to_world_matrix"]
point1 = dp.image_bytes_to_point_cloud_intrinsic_matrix(
    image_rgb, image_depth_exr, nd_intrinsic_matrix, local_to_world_matrix
)

# Capture data from the second camera
camera2 = env.GetAttr(698550)
camera2.GetDepthEXR(intrinsic_matrix=nd_intrinsic_matrix)
camera2.GetRGB(intrinsic_matrix=nd_intrinsic_matrix)
camera2.GetID(intrinsic_matrix=nd_intrinsic_matrix)
env.step()

# Process the captured data from the second camera
image_rgb = camera2.data["rgb"]
image_depth_exr = camera2.data["depth_exr"]
local_to_world_matrix = camera2.data["local_to_world_matrix"]
point2 = dp.image_bytes_to_point_cloud_intrinsic_matrix(
    image_rgb, image_depth_exr, nd_intrinsic_matrix, local_to_world_matrix
)

# Close the environment
env.close()

# Transform point clouds to Open3D space and visualize
point1.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point2.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame()
o3d.visualization.draw_geometries([point1, point2, coordinate_frame])
