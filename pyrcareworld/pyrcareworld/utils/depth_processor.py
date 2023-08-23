import math
import os
import os.path as osp
import numpy as np
import open3d as o3d
import cv2
import tempfile


def image_bytes_to_point_cloud(
    rgb_bytes: bytes, depth_bytes: bytes, fov: float, extrinsic_matrix: np.ndarray
):
    """
    Convert bytes to images, then convert them into point cloud
    """
    image_rgb = np.frombuffer(rgb_bytes, dtype=np.uint8)
    image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
    image_rgb = np.transpose(image_rgb, [1, 0, 2])

    # image_depth = np.frombuffer(depth_bytes, dtype=np.float16)
    # image_depth = cv2.imdecode(image_depth, cv2.IMREAD_UNCHANGED)

    # image_depth = np.frombuffer(depth_bytes, dtype=np.uint8)
    # image_depth = cv2.imdecode(image_depth, cv2.IMREAD_GRAYSCALE)
    # image_depth = image_depth * 5 / 255

    temp_file_path = osp.join(tempfile.gettempdir(), "temp_img.exr")
    with open(temp_file_path, "wb") as f:
        f.write(depth_bytes)
    image_depth = cv2.imread(temp_file_path, cv2.IMREAD_UNCHANGED)
    os.remove(temp_file_path)

    image_depth = np.transpose(image_depth, [1, 0])

    pcd = image_array_to_point_cloud(image_rgb, image_depth, fov, extrinsic_matrix)
    return pcd


def image_array_to_point_cloud(
    image_rgb: np.ndarray,
    image_depth: np.ndarray,
    fov: float,
    extrinsic_matrix: np.ndarray,
):
    points = depth_to_point_cloud(image_depth, fov=fov, organized=False)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    colors = image_rgb.reshape(-1, 3)
    pcd.colors = o3d.utility.Vector3dVector(colors.astype(np.float32) / 255.0)

    pcd.transform(extrinsic_matrix)

    return pcd


def depth_to_point_cloud(depth: np.ndarray, fov: float, organized=False):
    """
    Generate point cloud using depth image only.
        author: GraspNet baseline

        Args:
            depth: [numpy.ndarray, (W,H), numpy.float32] Depth image
            fov: [float] Field Of View for camera
            organized: [bool] Whether to keep the cloud in image shape (W,H,3)

        Return:
            cloud: [numpy.ndarray, (W,H,3)/(W*H,3), numpy.float32]
                generated cloud, (W,H,3) for organized=True, (W*H,3) for organized=False
    """
    width = depth.shape[0]
    height = depth.shape[1]
    cx = width / 2
    cy = height / 2
    xmap = np.arange(width)
    ymap = np.arange(height)
    xmap, ymap = np.meshgrid(xmap, ymap)
    xmap = xmap.T
    ymap = ymap.T

    fx = fy = height / (2 * math.tan(math.radians(fov / 2)))

    points_z = depth
    points_x = (xmap - cx) * points_z / fx
    points_y = (ymap - cy) * points_z / fy

    # radian_per_pixel = math.radians(fov / height)
    # points_x = np.sin(radian_per_pixel * (xmap - cx)) * depth
    # points_y = np.sin(radian_per_pixel * (ymap - cy)) * depth
    # points_z = depth ** 2 - points_x ** 2 - points_y ** 2
    # points_z[points_z < 0] = 0
    # points_z = np.sqrt(points_z)

    cloud = np.stack([points_x, -points_y, points_z], axis=-1)
    if not organized:
        cloud = cloud.reshape([-1, 3])

    return cloud


def image_bytes_to_point_cloud_intrinsic_matrix(
    rgb_bytes: bytes,
    depth_bytes: bytes,
    intrinsic_matrix: np.ndarray,
    extrinsic_matrix: np.ndarray,
):
    temp_file_path = osp.join(tempfile.gettempdir(), "temp_img.png")
    with open(temp_file_path, "wb") as f:
        f.write(rgb_bytes)
    color = o3d.io.read_image(temp_file_path)
    os.remove(temp_file_path)

    temp_file_path = osp.join(tempfile.gettempdir(), "temp_img.exr")
    with open(temp_file_path, "wb") as f:
        f.write(depth_bytes)
    # change .exr format to .png format
    depth_exr = cv2.imread(temp_file_path, cv2.IMREAD_UNCHANGED)
    os.remove(temp_file_path)
    # mask = np.asarray(o3d.io.read_image(osp.join(mask_path, video_name, view_name, base_name + '.png')))[:, :, 0]
    # foregound_mask = mask == 11
    depth_png = (depth_exr * 1000).astype(np.uint16)[:, :]
    # foreground_depth_png[~foregound_mask] = 0  # filter the background, only need foreground
    temp_file_path = osp.join(tempfile.gettempdir(), "temp_img.png")
    cv2.imwrite(temp_file_path, depth_png)
    depth = o3d.io.read_image(temp_file_path)
    os.remove(temp_file_path)

    pcd = image_open3d_to_point_cloud_intrinsic_matrix(
        color, depth, intrinsic_matrix, extrinsic_matrix
    )

    return pcd


def image_array_to_point_cloud_intrinsic_matrix(
    image_rgb: np.ndarray,
    image_depth: np.ndarray,
    intrinsic_matrix: np.ndarray,
    extrinsic_matrix: np.ndarray,
):
    temp_file_path = osp.join(tempfile.gettempdir(), "temp_img.png")

    image_rgb = np.transpose(image_rgb, [1, 0, 2])
    image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(temp_file_path, image_rgb)
    color = o3d.io.read_image(temp_file_path)

    # change .exr format to .png format
    depth_png = (image_depth * 1000).astype(np.uint16)[:, :]
    depth_png = np.transpose(depth_png, [1, 0])
    cv2.imwrite(temp_file_path, depth_png)
    depth = o3d.io.read_image(temp_file_path)

    os.remove(temp_file_path)

    pcd = image_open3d_to_point_cloud_intrinsic_matrix(
        color, depth, intrinsic_matrix, extrinsic_matrix
    )

    return pcd


def image_open3d_to_point_cloud_intrinsic_matrix(
    color: o3d.geometry.Image,
    depth: o3d.geometry.Image,
    intrinsic_matrix: np.ndarray,
    extrinsic_matrix: np.ndarray,
):
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

    # convter to unity space
    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    # camera to world in unity space
    pcd.transform(extrinsic_matrix)

    return pcd


def mask_point_cloud_with_id_color(
    pcd: o3d.geometry.PointCloud, image_mask: np.ndarray, color: list
):
    image_mask = image_mask.reshape(-1, 3)
    index = np.argwhere(image_mask == color)[:, 0]
    index = index[::3]
    d = np.array(pcd.points)[index]
    pcd.points = o3d.utility.Vector3dVector(d)
    c = np.array(pcd.colors)[index]
    pcd.colors = o3d.utility.Vector3dVector(c)
    return pcd


def mask_point_cloud_with_id_gray_color(
    pcd: o3d.geometry.PointCloud, image_mask: np.ndarray, color: int
):
    image_mask = image_mask.reshape(-1)
    index = np.argwhere(image_mask == color).reshape(-1)

    d = np.array(pcd.points)[index]
    pcd.points = o3d.utility.Vector3dVector(d)
    c = np.array(pcd.colors)[index]
    pcd.colors = o3d.utility.Vector3dVector(c)
    return pcd


def filter_active_depth_point_cloud_with_exact_depth_point_cloud(
    active_pcd: o3d.geometry.PointCloud,
    exact_pcd: o3d.geometry.PointCloud,
    max_distance: float = 0.05,
):
    active_point = np.array(active_pcd.points)
    exact_point = np.array(exact_pcd.points)
    # m = exact_point.shape[0]
    # n = active_point.shape[0]
    # duplicated_active_point = np.repeat(active_point, m).reshape((n, m, 3))
    # distance = np.linalg.norm(duplicated_active_point - exact_point, axis=-1)
    distance = np.linalg.norm(active_point - exact_point, axis=-1)
    # min_distance = np.min(distance, axis=1)
    index = np.argwhere(distance < max_distance).reshape(-1)
    pcd = o3d.geometry.PointCloud()
    d = np.array(active_pcd.points)[index]
    pcd.points = o3d.utility.Vector3dVector(d)
    c = np.array(active_pcd.colors)[index]
    pcd.colors = o3d.utility.Vector3dVector(c)
    return pcd


def filter_active_depth_point_cloud_with_exact_depth_point_cloud_bound(
    active_pcd: o3d.geometry.PointCloud,
    exact_pcd: o3d.geometry.PointCloud,
    max_distance: float = 0.05,
):
    active_point = np.array(active_pcd.points)
    exact_point = np.array(exact_pcd.points)
    x_all = exact_point[:, 0]
    y_all = exact_point[:, 1]
    z_all = exact_point[:, 2]
    x_max = np.max(x_all) + max_distance
    x_min = np.min(x_all) - max_distance
    y_max = np.max(y_all) + max_distance
    y_min = np.min(y_all) - max_distance
    z_max = np.max(z_all) + max_distance
    z_min = np.min(z_all) - max_distance
    active_x_all = active_point[:, 0].reshape(-1, 1)
    active_y_all = active_point[:, 1].reshape(-1, 1)
    active_z_all = active_point[:, 2].reshape(-1, 1)
    index_x_max = np.argwhere(active_x_all < x_max)
    index_y_max = np.argwhere(active_y_all < y_max)
    index_z_max = np.argwhere(active_z_all < z_max)
    index_x_min = np.argwhere(active_x_all > x_min)
    index_y_min = np.argwhere(active_y_all > y_min)
    index_z_min = np.argwhere(active_z_all > z_min)
    index = np.intersect1d(index_x_max, index_y_max)
    index = np.intersect1d(index, index_z_max)
    index = np.intersect1d(index, index_x_min)
    index = np.intersect1d(index, index_y_min)
    index = np.intersect1d(index, index_z_min)
    # index = np.argwhere(active_x_all < x_max and active_x_all > x_min and active_y_all < y_max and active_y_all > y_min and active_z_all < z_max and active_z_all > z_min)
    # index=[]
    # for i in range(active_point.shape[0]):
    # if active_point[i, 0] < x_max and active_point[i, 0] > x_min and active_point[i, 1] < y_max and active_point[i, 1] > y_min and active_point[i, 2] < z_max and active_point[i, 2] > z_min:
    # index.append(i)

    pcd = o3d.geometry.PointCloud()
    d = np.array(active_pcd.points)[index]
    pcd.points = o3d.utility.Vector3dVector(d)
    c = np.array(active_pcd.colors)[index]
    pcd.colors = o3d.utility.Vector3dVector(c)
    return pcd
