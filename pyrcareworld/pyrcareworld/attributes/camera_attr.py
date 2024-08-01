import numpy as np
import pyrcareworld.attributes as attr

class CameraAttr(attr.BaseAttr):
    """
    Camera attribute class, which can capture many kinds of screenshots
    of the scene in rcareworld.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

        :param data: Dictionary containing the message data.
        :return: A dict containing useful information of this class.
        :rtype: dict

        self.data['rgb']: The bytes of RGB image.
        self.data['normal']: The bytes of normal image.
        self.data['id_map']: The bytes of instance segmentation mask image.
        self.data['depth']: The bytes of depth image.
        self.data['depth_exr']: The bytes of depth image in EXR format.
        self.data['amodal_mask']: The bytes of amodal mask image.
        self.data['heat_map']: The bytes of heat map image.
        self.data['2d_bounding_box']: The 2D bounding box of objects in camera (image) coordinates.
        self.data['3d_bounding_box']: The 3D bounding box of objects in world coordinates.
        """
        super().parse_message(data)
        # if "rgb" in self.data:
        #     self.data["rgb"] = base64.b64decode(self.data["rgb"])
        # if "normal" in self.data:
        #     self.data["normal"] = base64.b64decode(self.data["normal"])
        # if "id_map" in self.data:
        #     self.data["id_map"] = base64.b64decode(self.data["id_map"])
        # if "depth" in self.data:
        #     self.data["depth"] = base64.b64decode(self.data["depth"])
        # if "depth_exr" in self.data:
        #     self.data["depth_exr"] = base64.b64decode(self.data["depth_exr"])
        # if "amodal_mask" in self.data:
        #     self.data["amodal_mask"] = base64.b64decode(self.data["amodal_mask"])
        # if "heat_map" in self.data:
        #     self.data["heat_map"] = base64.b64decode(self.data["heat_map"])

    def AlignView(self):
        """
        Make the camera in rcareworld align with the current view in GUI.
        """
        self._send_data("AlignView")

    def GetRGB(self, width: int = None, height: int = None, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the camera RGB image.

        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)

        self._send_data("GetRGB", intrinsic_matrix, int(width), int(height), float(fov))

    def GetNormal(self, width: int = None, height: int = None, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the normal image in world coordinates.

        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)
        self._send_data("GetNormal", intrinsic_matrix, int(width), int(height), float(fov))

    def GetID(self, width: int = None, height: int = None, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the instance segmentation mask image. The color for each pixel is computed from object ID, see `pyrcareworld.utils.rfunicerse_util.GetColorFromID` for more details.

        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)
        self._send_data("GetID", intrinsic_matrix, int(width), int(height), float(fov))

    def GetDepth(self, zero_dis: float = 0.0, one_dis: float = 1.0, width: int = None, height: int = None, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the depth 8-bit PNG image from the camera. Since each pixel of the depth image returned from this function is 8-bit, the user should limit the depth range (`zero_dis` and `one_dis`) for more accurate results.

        :param zero_dis: The minimum distance in calculation.
        :param one_dis: The maximum distance in calculation.
        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)
        self._send_data("GetDepth", float(zero_dis), float(one_dis), intrinsic_matrix, int(width), int(height), float(fov))

    def GetDepth16Bit(self, zero_dis: float = 0.0, one_dis: float = 1.0, width: int = None, height: int = None, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the depth 16-bit PNG image from the camera. Since each pixel of the depth image returned from this function is 16-bit, the user should limit the depth range (`zero_dis` and `one_dis`) for more accurate results.

        :param zero_dis: The minimum distance in calculation.
        :param one_dis: The maximum distance in calculation.
        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)
        self._send_data("GetDepth16Bit", float(zero_dis), float(one_dis), intrinsic_matrix, int(width), int(height), float(fov))

    def GetDepthEXR(self, width: int = None, height: int = None, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the depth EXR image from the camera. This function returns EXR format image bytes and each pixel is 32-bit.

        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)
        self._send_data("GetDepthEXR", intrinsic_matrix, int(width), int(height), float(fov))

    def GetAmodalMask(self, target_id: int, width: int = None, height: int = None, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the amodal mask image for the target object.

        :param target_id: The target object ID.
        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)
        self._send_data("GetAmodalMask", int(target_id), intrinsic_matrix, int(width), int(height), float(fov))

    def StartHeatMapRecord(self, targets_id: list):
        """
        Start recording heat map data for the specified targets.

        :param targets_id: List of target IDs to record heat map data for.
        """
        targets_id = [int(i) for i in targets_id]
        self._send_data("StartHeatMapRecord", targets_id)

    def EndHeatMapRecord(self):
        """
        End the heat map recording.
        """
        self._send_data("EndHeatMapRecord")

    def GetHeatMap(self, width: int = None, height: int = None, radius: int = 50, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the heat map image.

        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param radius: The radius of the heat map.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)
        self._send_data("GetHeatMap", int(radius), intrinsic_matrix, int(width), int(height), float(fov))

    def Get2DBBox(self, width: int = None, height: int = None, fov: float = 60.0, intrinsic_matrix: np.ndarray = None):
        """
        Get the 2D bounding box of objects in the current camera view.

        :param width: Int, the width of the image.
        :param height: Int, the height of the image.
        :param fov: Float, the field of view for the camera.
        :param intrinsic_matrix: A ndarray of shape 3x3, representing the camera intrinsic matrix. When this parameter is passed, `width`, `height`, and `fov` will be ignored.
        """
        if intrinsic_matrix is None:
            if width is None:
                width = 512
            if height is None:
                height = 512
        else:
            if width is None:
                width = int(intrinsic_matrix[0, 2] * 2)
            if height is None:
                height = int(intrinsic_matrix[1, 2] * 2)
        self._send_data("Get2DBBox", intrinsic_matrix, int(width), int(height), float(fov))

    def Get3DBBox(self):
        """
        Get the 3D bounding box of objects in world coordinates.
        """
        self._send_data("Get3DBBox")
