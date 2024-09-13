import math
import os
import random

import numpy as np
import open3d as o3d
import cv2
import tempfile


def image_bytes_to_point_cloud(
    rgb_bytes: bytes, depth_bytes: bytes, fov: float, local_to_world_matrix: np.ndarray
) -> o3d.geometry.PointCloud:
    """
    Use the raw bytes of RGB image and depth image, as well as the camera
    FOV and extrinsic matrix to generate a point cloud in global coordinate.

    :param rgb_bytes: Bytes, raw bytes of RGB image.
    :param depth_bytes: Bytes, raw bytes of depth image, EXR format.
    :param fov: Float, camera Field Of View (FOV).
    :param local_to_world_matrix: Numpy.ndarray, the local_to_world_matrix of the camera.
    :return: open3d.geometry.PointCloud, The point cloud.
    """
    image_rgb = np.frombuffer(rgb_bytes, dtype=np.uint8)
    image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)

    temp_file_path = os.path.join(
        tempfile.gettempdir(), f"temp_img_{int(random.uniform(10000000, 99999999))}.exr"
    )
    with open(temp_file_path, "wb") as f:
        f.write(depth_bytes)
    image_depth = cv2.imread(temp_file_path, cv2.IMREAD_UNCHANGED)
    os.remove(temp_file_path)

    pcd = image_array_to_point_cloud(image_rgb, image_depth, fov, local_to_world_matrix)
    return pcd


def image_array_to_point_cloud(
    image_rgb: np.ndarray,
    image_depth: np.ndarray,
    fov: float,
    local_to_world_matrix: np.ndarray,
) -> o3d.geometry.PointCloud:
    """
    Use the RGB image and depth image, as well as the camera
    FOV and extrinsic matrix to generate a point cloud in global coordinate.

    :param image_rgb: Numpy.ndarray, in shape (H, W, 3), the RGB image.
    :param image_depth: Numpy.ndarray, in shape (H, W, 3), the depth image.
    :param fov: Float, camera Field Of View (FOV).
    :param local_to_world_matrix: Numpy.ndarray, the local_to_world_matrix of the camera.
    :return: open3d.geometry.PointCloud, The point cloud.
    """
    points = depth_to_point_cloud(image_depth, fov=fov)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    colors = image_rgb.reshape(-1, 3)
    pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float32) / 255.0)

    pcd.transform(local_to_world_matrix)

    return pcd


def depth_to_point_cloud(depth: np.ndarray, fov: float) -> np.ndarray:
    """
    Use the depth image and the camera FOV to generate a point cloud in
    camera coordinate.

    :param depth: Numpy.ndarray, in shape (H, W, 3), the depth image.
    :param fov: Float, camera Field Of View (FOV).
    :return: np.ndarray, The point cloud.
    """
    height = depth.shape[0]
    width = depth.shape[1]

    cy = height / 2
    cx = width / 2

    xmap = np.arange(width)
    ymap = np.arange(height)
    xmap, ymap = np.meshgrid(xmap, ymap)

    fx = fy = height / (2 * math.tan(math.radians(fov / 2)))

    points_z = depth
    points_x = (xmap - cx) * points_z / fx
    points_y = (ymap - cy) * points_z / fy

    cloud = np.stack([points_x, -points_y, points_z], axis=-1)
    cloud = cloud.reshape([-1, 3])

    return cloud


def image_array_to_point_cloud_intrinsic_matrix(
    image_rgb: np.ndarray,
    image_depth: np.ndarray,
    intrinsic_matrix: np.ndarray,
    local_to_world_matrix: np.ndarray,
) -> o3d.geometry.PointCloud:
    """
    Use the RGB image and depth image, as well as the camera
    intrinsic matrix and extrinsic matrix to generate a point cloud in global coordinate.

    :param image_rgb: Numpy.ndarray, in shape (H, W, 3) [int][0-255], the RGB image.
    :param image_depth: Numpy.ndarray, in shape (H, W, 3) [float][real distance/unit meter], the depth image.
    :param intrinsic_matrix: Numpy.ndarray, in shape (3, 3), the intrinsic matrix of the camera.
    :param local_to_world_matrix: Numpy.ndarray, in shape (4, 4), the local_to_world_matrix of the camera.
    :return: open3d.geometry.PointCloud, The point cloud in Unity Space.
    """
    H, W = image_depth.shape
    fx, fy = intrinsic_matrix[0, 0], intrinsic_matrix[1, 1]
    cx, cy = intrinsic_matrix[0, 2], intrinsic_matrix[1, 2]

    u, v = np.meshgrid(np.arange(W), np.arange(H))

    x = (u - cx) / fx
    y = (v - cy) / fy

    z = image_depth

    X = x * z
    Y = y * z
    Z = z

    points = np.stack((X, Y, Z), axis=-1)
    points = points.reshape([-1, 3])
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)
    point_cloud.colors = o3d.utility.Vector3dVector(image_rgb.reshape(-1, 3) / 255.0)
    # convert to unity space
    point_cloud.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    # camera to world in unity space
    point_cloud.transform(local_to_world_matrix)
    return point_cloud


def image_bytes_to_point_cloud_intrinsic_matrix(
    rgb_bytes: bytes,
    depth_bytes: bytes,
    intrinsic_matrix: np.ndarray,
    local_to_world_matrix: np.ndarray,
) -> o3d.geometry.PointCloud:
    """
    Use the raw bytes of RGB image and depth image, as well as the camera
    intrinsic matrix and extrinsic matrix to generate a point cloud in global coordinate.

    :param rgb_bytes: Bytes, raw bytes of RGB image.
    :param depth_bytes: Bytes, raw bytes of depth image, EXR format.
    :param intrinsic_matrix: Numpy.ndarray, the intrinsic matrix of the camera.
    :param local_to_world_matrix: Numpy.ndarray, the local_to_world_matrix of the camera.
    :return: open3d.geometry.PointCloud, The point cloud.
    """
    image_rgb = np.frombuffer(rgb_bytes, dtype=np.uint8)
    image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)

    temp_file_path = os.path.join(
        tempfile.gettempdir(), f"temp_img_{int(random.uniform(10000000, 99999999))}.exr"
    )
    with open(temp_file_path, "wb") as f:
        f.write(depth_bytes)
    depth_exr = cv2.imread(temp_file_path, cv2.IMREAD_UNCHANGED)
    os.remove(temp_file_path)

    return image_array_to_point_cloud_intrinsic_matrix(image_rgb, depth_exr, intrinsic_matrix, local_to_world_matrix)


def image_open3d_to_point_cloud_intrinsic_matrix(
    color: o3d.geometry.Image,
    depth: o3d.geometry.Image,
    intrinsic_matrix: np.ndarray,
    local_to_world_matrix: np.ndarray,
) -> o3d.geometry.PointCloud:
    """
    Use the RGB image and depth image in open3d.geometry.Image format, as well as the camera
    intrinsic matrix and extrinsic matrix to generate a point cloud in global coordinate.

    :param color: open3d.geometry.Image, the RGB image.
    :param depth: open3d.geometry.Image, the depth image.
    :param intrinsic_matrix: Numpy.ndarray, the intrinsic matrix of the camera.
    :param local_to_world_matrix: Numpy.ndarray, the local_to_world_matrix of the camera.
    :return: open3d.geometry.PointCloud, The point cloud.
    """
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color, depth, depth_trunc=20, convert_rgb_to_intensity=False
    )

    intrinsic_matrix = o3d.camera.PinholeCameraIntrinsic(
        int(intrinsic_matrix[0, 2] * 2),
        int(intrinsic_matrix[1, 2] * 2),
        intrinsic_matrix[0, 0],
        intrinsic_matrix[1, 1],
        intrinsic_matrix[0, 2],
        intrinsic_matrix[1, 2],
    )

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd_image, intrinsic_matrix, project_valid_depth_only=False
    )

    # convert to unity space
    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    # camera to world in unity space
    pcd.transform(local_to_world_matrix)

    return pcd


def mask_point_cloud_with_id_color(
    pcd: o3d.geometry.PointCloud, image_mask: np.ndarray, color: list
) -> o3d.geometry.PointCloud:
    """
    Mask the point cloud with given segmentation masks and target color.

    :param pcd: open3d.geometry.PointCloud, the point cloud.
    :param image_mask: numpy.ndarray, the segmentation mask in shape (H, W, 3).
    :param color: List, the target color list.
    :return: open3d.geometry.PointCloud, The point cloud.
    """
    image_mask = image_mask.reshape(-1, 3)
    index = np.argwhere(image_mask == color)[:, 0]
    index = index[::3]
    id_pcd = o3d.geometry.PointCloud()
    d = np.array(pcd.points)[index]
    id_pcd.points = o3d.utility.Vector3dVector(d)
    c = np.array(pcd.colors)[index]
    id_pcd.colors = o3d.utility.Vector3dVector(c)
    return id_pcd


def mask_point_cloud_with_id_gray_color(
    pcd: o3d.geometry.PointCloud, image_mask: np.ndarray, color: int
) -> o3d.geometry.PointCloud:
    """
    Mask the point cloud with given gray-scale segmentation masks and target color.

    :param pcd: open3d.geometry.PointCloud, the point cloud.
    :param image_mask: numpy.ndarray, the segmentation mask in shape (H, W).
    :param color: Int, the target gray-scale color.
    :return: open3d.geometry.PointCloud, The point cloud.
    """
    image_mask = image_mask.reshape(-1)
    index = np.argwhere(image_mask == color).reshape(-1)
    id_pcd = o3d.geometry.PointCloud()
    d = np.array(pcd.points)[index]
    id_pcd.points = o3d.utility.Vector3dVector(d)
    c = np.array(pcd.colors)[index]
    id_pcd.colors = o3d.utility.Vector3dVector(c)
    return id_pcd


def filter_active_depth_point_cloud_with_exact_depth_point_cloud(
    active_pcd: o3d.geometry.PointCloud,
    exact_pcd: o3d.geometry.PointCloud,
    max_distance: float = 0.05,
) -> o3d.geometry.PointCloud:
    """
    Use exact point cloud to filter IR-based active point cloud based on a tolerance distance.

    :param active_pcd: open3d.geometry.PointCloud, the IR-based active point cloud.
    :param exact_pcd: open3d.geometry.PointCloud, the exact point cloud.
    :param max_distance: float, the maximum tolerance distance.
    :return: open3d.geometry.PointCloud, The point cloud.
    """
    active_point = np.array(active_pcd.points)
    exact_point = np.array(exact_pcd.points)
    distance = np.linalg.norm(active_point - exact_point, axis=-1)
    index = np.argwhere(distance < max_distance).reshape(-1)
    filter_pcd = o3d.geometry.PointCloud()
    d = np.array(active_pcd.points)[index]
    filter_pcd.points = o3d.utility.Vector3dVector(d)
    c = np.array(active_pcd.colors)[index]
    filter_pcd.colors = o3d.utility.Vector3dVector(c)
    return filter_pcd
