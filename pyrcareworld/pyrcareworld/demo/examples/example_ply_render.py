import os
import sys
import pyrcareworld.attributes as attr

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.demo import mesh_path


from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "Player/Player.x86_64")

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
