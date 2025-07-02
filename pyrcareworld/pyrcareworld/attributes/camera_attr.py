import numpy as np
import pyrcareworld.attributes as attr
from scipy.spatial.transform import Rotation as R

class CameraAttr(attr.BaseAttr):
    """
    Camera class. This class is used to control the camera and obtain visual information from the simulation environment.
    
    The data stored in self.data is a dictionary containing the following keys:
        - 'name': The name of the object.
        - 'position': The position of the object in world coordinates.
        - 'rotation': The euler angle of the object in world coordinates.
        - 'quaternion': The quaternion of the object in world coordinates.
        - 'local_position': The position of the object in its parent's local coordinates.
        - 'local_rotation': The euler angle of the object in its parent's local coordinates.
        - 'local_quaternion': The quaternion of the object in its parent's local coordinates.
        - 'local_to_world_matrix': The transformation matrix from local to world coordinates.
        - 'result_local_point': The result of transforming the object from local to world coordinates.
        - 'result_world_point': The result of transforming the object from world to local coordinates.
    """

    def AlignView(self):
        """
        Make the camera in rcareworld align with the current view in GUI.
        """
        self._send_data("AlignView")
    
    def GetIntrinsic(self, width: int = 512, height: int = 512, fov: float = 60.0) -> np.ndarray:
        """
        Calculate the intrinsic camera matrix based on image size and field of view.

        :param width: Image width in pixels.
        :param height: Image height in pixels.
        :param fov: Field of view in degrees.
        :return: 3x3 numpy array representing the intrinsic matrix.
        """
        # Convert FOV from degrees to radians
        fov_rad = np.deg2rad(fov)

        # Calculate focal length in pixels
        f = 0.5 * width / np.tan(0.5 * fov_rad)

        # Assume principal point is at the image center
        cx = width / 2
        cy = height / 2

        intrinsic_matrix = np.array([
            [f, 0, cx],
            [0, f, cy],
            [0, 0, 1]
        ])

        return intrinsic_matrix
    
    def GetExtrinsic(self, position: np.ndarray, quaternion: np.ndarray) -> np.ndarray:
        """
        Calculate the camera extrinsic matrix from position and orientation (quaternion).

        :param position: Camera position in world coordinates (3,).
        :param quaternion: Camera orientation as a quaternion (x, y, z, w).
        :return: 4x4 numpy array representing the extrinsic matrix.
        """
        # Convert quaternion to rotation matrix
        rotation = R.from_quat(quaternion).as_matrix()

        # Build the extrinsic matrix [R | t]
        extrinsic = np.eye(4)
        extrinsic[:3, :3] = rotation
        extrinsic[:3, 3] = position

        return extrinsic
    


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
