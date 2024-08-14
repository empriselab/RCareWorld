print("""
This script demonstrates the visualization of a point cloud in the RCareWorld environment using a PLY file.

What it Implements:
- Initializes the environment and creates a PointCloud object.
- =====***ONLY a pointcloud will be rendered.***=====
- Loads and displays a point cloud from a specified PLY file.
- Adjusts the transform and radius of the point cloud for visualization purposes.

What the Functionality Covers:
- Understanding how to load and visualize point clouds in RCareWorld.
- Demonstrates basic transformations and radius adjustments for point cloud data.

Required Operations:
- Visualization: Displays the point cloud with specified transformations and settings.
""")

import os
import sys
import time
import pyrcareworld.attributes as attr

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.demo import mesh_path


from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

time.sleep(5)
# Initialize the environment
env = RCareWorld(executable_file=player_path)

# Set the background color of the view
env.SetViewBackGround([0.0, 0.0, 0.0])

# Create an instance of a PointCloud object
point_cloud = env.InstanceObject(
    name="PointCloud", id=123456, attr_type=attr.PointCloudAttr
)

# Show the point cloud from the specified PLY file
point_cloud.ShowPointCloud(ply_path=os.path.join(mesh_path, "1.ply"))

# Set the transform and radius of the point cloud
point_cloud.SetTransform(rotation=[-90, 0, 0])
point_cloud.SetRadius(radius=0.001)

# End the environment session
env.Pend()
env.close()
