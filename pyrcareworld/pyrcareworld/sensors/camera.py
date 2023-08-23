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
        width: int = 480,
        height: int = 480,
        fov: float = 60,
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

    def initializeRGBWithIntrinsic(self):
        """
        Initialize the camera for RGB images with the intrinsic matrix
        """
        self.env.instance_channel.set_action(
            "GetRGB", id=self.id, intrinsic_matrix=self.intrinsic_matrix
        )
        self.env._step()
        self.is_initialized.append("rgb_intrinsic")

    def initializeRGB(self):
        """
        Initialize the camera for RGB images with width, height, and fov
        """
        if self.fov is not None:
            self.env.instance_channel.set_action(
                "GetRGB", id=self.id, width=self.width, height=self.height, fov=self.fov
            )
            self.is_initialized.append("rgb_fov")
        else:
            self.env.instance_channel.set_action(
                "GetRGB", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("rgb_wh")
        self.env._step()

    def getRGB(self):
        """
        Returns the RGB image as an image array
        """
        image_byte = self.env.instance_channel.data[self.id]["rgb"]
        image_rgb = np.frombuffer(image_byte, dtype=np.uint8)
        image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
        return image_rgb

    def initializeDepthEXRWithIntrinsic(self):
        """
        Initialize the camera for depth images with the intrinsic matrix
        """
        self.env.instance_channel.set_action(
            "GetDepthEXR",
            id=self.id,
            intrinsic_matrix=self.intrinsic_matrix,
        )
        self.env._step()
        self.is_initialized.append("depth_intrinsic")

    def initializeDepthEXR(self):
        """
        Initialize the camera for depth images with width, height, and fov
        """
        if self.fov is not None:
            self.env.instance_channel.set_action(
                "GetDepthEXR",
                id=self.id,
                width=self.width,
                height=self.height,
                fov=self.fov,
            )
            self.is_initialized.append("depth_fov")
        else:
            self.env.instance_channel.set_action(
                "GetDepthEXR", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("depth_wh")
        self.env._step()

    def getDepthEXR(self):
        """
        Returns the depth image as a numpy array
        """
        depth = self.env.instance_channel.data[self.id]["depth_exr"]
        return depth

    def initializeNormalWithIntrinsic(self):
        """
        Initialize the camera for surface normals with the intrinsic matrix
        """
        self.env.instance_channel.set_action(
            "GetNormal", id=self.id, intrinsic_matrix=self.intrinsic_matrix
        )
        self.env._step()
        self.is_initialized.append("normal_intrinsic")

    def initializeNormal(self):
        """
        Initialize the camera for surface normals with width, height, and fov
        """
        if self.fov is not None:
            self.env.instance_channel.set_action(
                "GetNormal",
                id=self.id,
                width=self.width,
                height=self.height,
                fov=self.fov,
            )
            self.is_initialized.append("normal_fov")
        else:
            self.env.instance_channel.set_action(
                "GetNormal", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("normal_wh")
        self.env._step()

    def getNormal(self):
        """
        Returns the surface normals as a numpy array
        """
        normal = self.env.instance_channel.data[self.id]["normal"]
        return normal

    def initializeInstanceMaskWithIntrinsic(self):
        """
        Initialize the camera for instance masks with the intrinsic matrix
        """
        self.env.instance_channel.set_action(
            "GetID", id=self.id, intrinsic_matrix=self.intrinsic_matrix
        )
        self.env._step()
        self.is_initialized.append("instance_intrinsic")

    def initializeInstanceMask(self, w, h, fov=None):
        """
        Initialize the camera for instance masks with width, height, and fov
        """
        if fov is not None:
            self.env.instance_channel.set_action(
                "GetID", id=self.id, width=self.width, height=self.height, fov=self.fov
            )
            self.is_initialized.append("instance_fov")
        else:
            self.env.instance_channel.set_action(
                "GetID", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("instance_wh")
        self.env._step()

    def getInstanceMask(self):
        """
        Returns the instance mask as a numpy array
        """
        image_id = self.env.instance_channel.data[self.id]["id_map"]
        image_id = np.frombuffer(image_id, dtype=np.uint8)
        image_id = cv2.imdecode(image_id, cv2.IMREAD_COLOR)
        return image_id

    def initializeAmodalMaskWithIntrinsic(self):
        """
        Initialize the camera for amodal masks with the intrinsic matrix
        """
        self.env.instance_channel.set_action(
            "GetAmodalMask", id=self.id, intrinsic_matrix=self.intrinsic_matrix
        )
        self.env._step()
        self.is_initialized.append("amodal_intrinsic")

    def initializeAmodalMask(self, w, h, fov=None):
        """
        Initialize the camera for amodal masks with width, height, and fov
        """
        if fov is not None:
            self.env.instance_channel.set_action(
                "GetAmodalMask",
                id=self.id,
                width=self.width,
                height=self.height,
                fov=self.fov,
            )
            self.is_initialized.append("amodal_fov")
        else:
            self.env.instance_channel.set_action(
                "GetAmodalMask", id=self.id, width=self.width, height=self.height
            )
            self.is_initialized.append("amodal_wh")
        self.env._step()

    def getAmodalMask(self):
        """
        Returns the amodal mask as a numpy array
        """
        image_id = self.env.instance_channel.data[self.id]["amodal_mask"]
        image_id = np.frombuffer(image_id, dtype=np.uint8)
        image_id = cv2.imdecode(image_id, cv2.IMREAD_COLOR)
        return image_id

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
        self.env._step()
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
