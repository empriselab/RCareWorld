from pyrcareworld.objects import RCareWorldBaseObject
import cv2
import numpy as np

try:
    import open3d as o3d
except ImportError:
    print("This feature requires open3d, please install with `pip install open3d`")
    raise

import pyrcareworld.utils.depth_processor as dp


class Camera(RCareWorldBaseObject):
    def __init__(
        self,
        env,
        id: int,
        name: str,
        intrinsic_matrix=[600, 0, 0, 0, 600, 0, 240, 240, 1],
        width: int = 256,
        height: int = 256,
        fov: float = None,
        is_in_scene: bool = True,
    ):
        super().__init__(env=env, id=id, name=name, is_in_scene=is_in_scene)
        self.intrinsic_matrix = intrinsic_matrix
        self.width = width
        self.height = height
        self.fov = fov
        self.is_initialized = []

    def getCameraInfo(self):
        """
        Returns a dict with width, height, and fov
        """
        w = self.env.instance_channel.data[self.id]["width"]
        h = self.env.instance_channel.data[self.id]["height"]
        fov = self.env.instance_channel.data[self.id]["fov"]
        info = {}
        info["width"] = w
        info["height"] = h
        info["fov"] = fov
        return info

    def getRGB(self, mode = "wh"):
        """
        Initialize the camera for RGB images with width, height, and fov, or intrinsic matrix
        mode = "fov" or "intrinsic" or "wh"
        """
        assert mode in ["fov", "intrinsic", "wh"], "mode should be 'fov' or 'intrinsic' or 'wh'"
        if mode == "fov":
            self.env.instance_channel.set_action(
                "GetRGB", id=self.id, width=self.width, height=self.height, fov=self.fov
            )
            self.is_initialized.append("rgb_fov")
        elif mode == "wh":
            self.env.instance_channel.set_action(
                "GetRGB", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("rgb_wh")
        elif mode == "intrinsic":
            self.env.instance_channel.set_action(
                "GetRGB", id=self.id, intrinsic_matrix=self.intrinsic_matrix
            )
            self.is_initialized.append("rgb_intrinsic")
        self.env._step()
        image_byte = self.env.instance_channel.data[self.id]["rgb"]
        image_rgb = np.frombuffer(image_byte, dtype=np.uint8)
        reshaped_image_rgb = image_rgb.reshape(self.height, self.width, 3)
        # upside down and convert bgr to rgb
        reshaped_image_rgb = np.flipud(reshaped_image_rgb)[:, :, ::-1]
        return reshaped_image_rgb

    def getDepthEXR(self, mode = "wh"):
        """
        Initialize the camera for depth images in EXR format with width, height, and fov, or intrinsic matrix
        mode = "fov" or "intrinsic" or "wh"
        """
        assert mode in ["fov", "intrinsic", "wh"], "mode should be 'fov' or 'intrinsic' or 'wh'"
        if mode == "fov":
            self.env.instance_channel.set_action(
                "GetDepthEXR", id=self.id, width=self.width, height=self.height, fov=self.fov
            )
            self.is_initialized.append("depth_fov")
        elif mode == "wh":
            self.env.instance_channel.set_action(
                "GetDepthEXR", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("depth_wh")
        elif mode == "intrinsic":
            self.env.instance_channel.set_action(
                "GetDepthEXR", id=self.id, intrinsic_matrix=self.intrinsic_matrix
            )
            self.is_initialized.append("depth_intrinsic")
        self.env._step()
        depth = self.env.instance_channel.data[self.id]["depth_exr"]
        depth = np.frombuffer(depth, dtype=np.float32)
        reshaped_image_depth = depth.reshape(self.height, self.width)
        return reshaped_image_depth
    
    def getNormal(self, mode = "wh"):
        """
        Initialize the camera for surface normals with width, height, and fov, or intrinsic matrix
        mode = "fov" or "intrinsic" or "wh"
        """
        assert mode in ["fov", "intrinsic", "wh"], "mode should be 'fov' or 'intrinsic' or 'wh'"
        if mode == "fov":
            self.env.instance_channel.set_action(
                "GetNormal", id=self.id, width=self.width, height=self.height, fov=self.fov
            )
            self.is_initialized.append("normal_fov")
        elif mode == "wh":
            self.env.instance_channel.set_action(
                "GetNormal", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("normal_wh")
        elif mode == "intrinsic":
            self.env.instance_channel.set_action(
                "GetNormal", id=self.id, intrinsic_matrix=self.intrinsic_matrix
            )
            self.is_initialized.append("normal_intrinsic")
        self.env._step()
        normal = self.env.instance_channel.data[self.id]["normal"]
        normal = np.frombuffer(normal, dtype=np.uint8)
        reshaped_image_normal = normal.reshape(self.height, self.width, 3)
        return reshaped_image_normal
    
    def getInstanceMask(self, mode = "wh"):
        """
        Initialize the camera for instance masks with width, height, and fov, or intrinsic matrix
        mode = "fov" or "intrinsic" or "wh"
        """
        assert mode in ["fov", "intrinsic", "wh"], "mode should be 'fov' or 'intrinsic' or 'wh'"
        if mode == "fov":
            self.env.instance_channel.set_action(
                "GetID", id=self.id, width=self.width, height=self.height, fov=self.fov
            )
            self.is_initialized.append("instance_fov")
        elif mode == "wh":
            self.env.instance_channel.set_action(
                "GetID", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("instance_wh")
        elif mode == "intrinsic":
            self.env.instance_channel.set_action(
                "GetID", id=self.id, intrinsic_matrix=self.intrinsic_matrix
            )
            self.is_initialized.append("instance_intrinsic")
        self.env._step()
        image_id = self.env.instance_channel.data[self.id]["id_map"]
        image_id = np.frombuffer(image_id, dtype=np.uint8)
        reshaped_image_id = image_id.reshape(self.height, self.width, 3)
        return reshaped_image_id
    
    def getAmodalInstanceMask(self, mode = "wh"):
        """
        Initialize the camera for amodal instance masks with width, height, and fov, or intrinsic matrix
        mode = "fov" or "intrinsic" or "wh"
        """
        assert mode in ["fov", "intrinsic", "wh"], "mode should be 'fov' or 'intrinsic' or 'wh'"
        if mode == "fov":
            self.env.instance_channel.set_action(
                "GetAmodalMask", id=self.id, width=self.width, height=self.height, fov=self.fov
            )
            self.is_initialized.append("amodal_instance_fov")
        elif mode == "wh":
            self.env.instance_channel.set_action(
                "GetAmodalMask", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("amodal_instance_wh")
        elif mode == "intrinsic":
            self.env.instance_channel.set_action(
                "GetAmodalMask", id=self.id, intrinsic_matrix=self.intrinsic_matrix
            )
            self.is_initialized.append("amodal_instance_intrinsic")
        self.env._step()
        image_id = self.env.instance_channel.data[self.id]["amodal_mask"]
        image_id = np.frombuffer(image_id, dtype=np.uint8)
        reshaped_image_id = image_id.reshape(self.height, self.width, 4)
        return reshaped_image_id


    def initializeActiveDepthWithIntrinsic(self, ir_intrinsic_matrix):
        """
        Initialize the camera for active depth with the intrinsic matrix and the ir intrinsic matrix
        The ir intrinsic matrix should be a list of 9 elements like ir_intrinsic_matrix = [480, 0, 0, 0, 480, 0, 240, 240, 1]
        """
        self.env.instance_channel.set_action(
            "GetActiveDepth",
            id=self.id,
            main_intrinsic_matrix=self.intrinsic_matrix,
            ir_intrinsic_matrix=ir_intrinsic_matrix,
        )
        self.is_initialized.append("active_intrinsic")

    def getActiveDepth(self):
        """
        Returns the active depth as a numpy array
        """
        depth = self.env.instance_channel.data[self.id]["active_depth"]
        image_active_depth = np.transpose(depth, [1, 0])
        return image_active_depth

    def getLocalToWorldMatrix(self):
        """
        Returns the local to world matrix
        """
        local_to_world_matrix = self.env.instance_channel.data[self.id][
            "local_to_world_matrix"
        ]
        local_to_world_matrix = np.reshape(local_to_world_matrix, [4, 4]).T
        return local_to_world_matrix

    def _intrinsic_to_nd_intrinsic(self, intrinsic_matrix):
        nd_main_intrinsic_matrix = np.reshape(intrinsic_matrix, [3, 3]).T
        return nd_main_intrinsic_matrix

    def getPointCloudWithDepth(self):
        """
        Returns the point cloud as a numpy array
        """
        image_byte = self.env.instance_channel[self.obejct_id]["rgb"]
        image_depth_exr = self.env.instance_channel[self.obejct_id]["depth_exr"]
        nd_main_intrinsic_matrix = self._intrinsic_to_nd_intrinsic(
            self.intrinsic_matrix
        )
        local_to_world_matrix = self.getLocalToWorldMatrix()
        point_cloud = dp.image_bytes_to_point_cloud_intrinsic_matrix(
            image_byte, image_depth_exr, nd_main_intrinsic_matrix, local_to_world_matrix
        )
        return point_cloud

    def getPointCloudWithActiveDepth(self):
        """
        Returns the point cloud as a numpy array
        """
        image_byte = self.env.instance_channel[self.id]["rgb"]
        image_active_depth = self.env.instance_channel[self.id]["active_depth"]
        image_active_depth = np.transpose(image_active_depth, [1, 0])
        nd_main_intrinsic_matrix = self._intrinsic_to_nd_intrinsic(
            self.intrinsic_matrix
        )
        local_to_world_matrix = self.getLocalToWorldMatrix()
        point_cloud = dp.image_bytes_to_point_cloud_intrinsic_matrix(
            image_byte,
            image_active_depth,
            nd_main_intrinsic_matrix,
            local_to_world_matrix,
        )
        return point_cloud

    def visualizePointCloud(self, point_cloud, mode="unity"):
        """
        visualize pointcloud with open3D or in Unity Editor
        You need to install open3D to use this function
        @param point_cloud: point cloud data
        @param mode: 'o3d' or 'unity'
        """
        if mode == "o3d":
            pass
        elif mode == "unity":
            self.env.asset_channel.set_action(
                "InstanceObject", name="PointCloud", id=123456
            )
            self.env.instance_channel.set_action(
                "ShowPointCloud",
                id=123456,
                positions=np.array(point_cloud.points).reshape(-1).tolist(),
                colors=np.array(point_cloud.colors).reshape(-1).tolist(),
            )

    def attachToObject(self, id):
        """
        Attach the camera to the object
        """
        self.env.instance_channel.set_action("SetParent", id=self.id, parent_id=id)
