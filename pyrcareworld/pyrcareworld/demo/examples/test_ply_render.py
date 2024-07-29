import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pyrcareworld.attributes as attr
from pyrcareworld.envs.base_env import RCareWorld
from demo import mesh_path

def test_ply_render():
    """Tests rendering a ply pointcloud."""
    env = RCareWorld(graphics=False)
    env.SetViewBackGround([0.0, 0.0, 0.0])
    point_cloud = env.InstanceObject(
        name="PointCloud", id=123456, attr_type=attr.PointCloudAttr
    )
    point_cloud.ShowPointCloud(ply_path=os.path.join(mesh_path, "1.ply"))
    point_cloud.SetTransform(rotation=[-90, 0, 0])
    point_cloud.SetRadius(radius=0.001)

    env.close()
