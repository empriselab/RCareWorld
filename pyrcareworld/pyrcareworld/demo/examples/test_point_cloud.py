import os

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.utils.depth_processor as dp

try:
    import open3d as o3d
except ImportError:
    raise Exception(
        "This feature requires open3d, please install with `pip install open3d`"
    )

def test_point_cloud():
    """Tests for extracting and rendering a point cloud."""
    env = RCareWorld(scene_file="PointCloud.json", graphics=False)
    camera1 = env.GetAttr(698548)
    camera1.GetDepthEXR(width=1920, height=1080)
    camera1.GetRGB(width=1920, height=1080)
    camera1.GetID(width=1920, height=1080)
    env.step()

    image_rgb = camera1.data["rgb"]
    image_depth_exr = camera1.data["depth_exr"]
    fov = 60
    local_to_world_matrix = camera1.data["local_to_world_matrix"]
    point1 = dp.image_bytes_to_point_cloud(
        image_rgb, image_depth_exr, fov, local_to_world_matrix
    )

    camera2 = env.GetAttr(698550)
    camera2.GetDepthEXR(width=1920, height=1080)
    camera2.GetRGB(width=1920, height=1080)
    camera2.GetID(width=1920, height=1080)
    env.step()

    image_rgb = camera2.data["rgb"]
    image_depth_exr = camera2.data["depth_exr"]
    fov = 60
    local_to_world_matrix = camera2.data["local_to_world_matrix"]
    point2 = dp.image_bytes_to_point_cloud(
        image_rgb, image_depth_exr, fov, local_to_world_matrix
    )

    env.close()

    # unity space to open3d space and show
    point1.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    point2.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    coorninate = o3d.geometry.TriangleMesh.create_coordinate_frame()
    o3d.visualization.draw_geometries([point1, point2, coorninate])
