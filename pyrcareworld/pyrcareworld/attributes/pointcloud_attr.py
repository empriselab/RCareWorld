import numpy as np
import pyrcareworld.attributes as attr


class PointCloudAttr(attr.BaseAttr):
    """
    Point cloud rendering class.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by internal function.

        Returns:
            Dict: A dict containing useful information of this class.
        """
        super().parse_message(data)

    def ShowPointCloud(
        self,
        positions: np.ndarray = None,
        colors: np.ndarray = None,
        ply_path: str = None,
        radius: float = 0.01,
    ):
        """
        Display point cloud in Unity.

        Args:
            positions: A list of positions of points in a point cloud.
            colors: A list of colors of points (range [0, 1]) in a point cloud.
            ply_path: Str, the absolute path of `.ply` file. If this parameter is specified, `positions`
                and `colors` will be ignored.
            radius: Float, the radius of the point cloud.
        """
        self._send_data("ShowPointCloud", ply_path, positions, colors, radius)

    def SetRadius(self, radius: float):
        """
        Set the radius for points in a point cloud.

        Args:
            radius: Float, the radius.
        """
        self._send_data("SetRadius", radius)
