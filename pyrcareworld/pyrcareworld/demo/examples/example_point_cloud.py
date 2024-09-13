print("""
This script demonstrates the capture and processing of depth and RGB data from cameras in the RCareWorld environment to generate and visualize point clouds using Open3D.

What it Implements:
- Initializes the environment and sets up two cameras to capture depth, RGB, and ID data.
- Processes the captured data to generate point clouds using a specified field of view (FOV) and the local-to-world transformation matrix.
- Transforms the point clouds into Open3D's coordinate space and visualizes them.

What the Functionality Covers:
- Understanding how to capture and process depth and RGB data from cameras in RCareWorld.
- Demonstrates the integration of Open3D for 3D point cloud visualization and manipulation.

Required Operations:
- Data Capture: Captures depth, RGB, and ID images from multiple cameras.
- Data Processing: Converts the captured data into point clouds using field of view and transformation matrices.
- Visualization: Displays the point clouds in Open3D's visualization environment.
""")

import os
import sys
import pyrcareworld.utils.depth_processor as dp

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Enable OpenCV EXR support
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Ensure open3d is installed
try:
    import open3d as o3d
except ImportError:
    raise Exception(
        "This feature requires open3d, please install with `pip install open3d`"
    )


# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with the specified scene file
env = RCareWorld(scene_file="PointCloud.json", executable_file=player_path)

# Capture data from the first camera
camera1 = env.GetAttr(698548)
camera1.GetDepthEXR(width=1920, height=1080)
camera1.GetRGB(width=1920, height=1080)
camera1.GetID(width=1920, height=1080)
env.step()

# Process the captured data from the first camera
image_rgb = camera1.data["rgb"]
image_depth_exr = camera1.data["depth_exr"]
fov = 60
local_to_world_matrix = camera1.data["local_to_world_matrix"]
point1 = dp.image_bytes_to_point_cloud(
    image_rgb, image_depth_exr, fov, local_to_world_matrix
)

# Capture data from the second camera
camera2 = env.GetAttr(698550)
camera2.GetDepthEXR(width=1920, height=1080)
camera2.GetRGB(width=1920, height=1080)
camera2.GetID(width=1920, height=1080)
env.step()

# Process the captured data from the second camera
image_rgb = camera2.data["rgb"]
image_depth_exr = camera2.data["depth_exr"]
local_to_world_matrix = camera2.data["local_to_world_matrix"]
point2 = dp.image_bytes_to_point_cloud(
    image_rgb, image_depth_exr, fov, local_to_world_matrix
)

# Close the environment
env.close()

# Transform point clouds to Open3D space and visualize
point1.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
point2.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame()
o3d.visualization.draw_geometries([point1, point2, coordinate_frame])
