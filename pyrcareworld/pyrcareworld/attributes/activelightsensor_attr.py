import base64
import cv2
import numpy as np
import pyrcareworld.attributes as attr
import pyrcareworld.utils.active_depth_generate as active_depth


class ActiveLightSensorAttr(attr.CameraAttr):
    """
    Class of IR-based depth sensor, which can simulate the noise of
    real-world depth camera and produce depth image in similar pattern.
    """

    def __init__(self, env, id: int, data=None):
        """
        Initialize the ActiveLightSensorAttr.

        :param env: Environment object.
        :param id: ID of the sensor.
        :param data: Optional initial data.
        """
        super().__init__(env, id, data)
        self.main_intrinsic_matrix = np.eye(3)
        self.ir_intrinsic_matrix = np.eye(3)

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

        :param data: Dictionary containing the message data.
        :return: A dict containing useful information of this class.
        :rtype: dict
        """
        super().parse_message(data)
        if "ir_left" in self.data and "ir_right" in self.data:
            self.data["ir_left"] = base64.b64decode(self.data["ir_left"])
            self.data["ir_right"] = base64.b64decode(self.data["ir_right"])

            image_left = np.frombuffer(self.data["ir_left"], dtype=np.uint8)
            image_left = cv2.imdecode(image_left, cv2.IMREAD_COLOR)[..., 2]
            image_right = np.frombuffer(self.data["ir_right"], dtype=np.uint8)
            image_right = cv2.imdecode(image_right, cv2.IMREAD_COLOR)[..., 2]
            left_extrinsic_matrix = np.array(
                [
                    [0.0, -1.0, 0.0, -0.0175],
                    [0.0, 0.0, -1.0, 0.0],
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            )
            right_extrinsic_matrix = np.array(
                [
                    [0.0, -1.0, 0.0, -0.072],
                    [0.0, 0.0, -1.0, 0.0],
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            )
            main_extrinsic_matrix = np.array(
                [
                    [0.0, -1.0, 0.0, 0.0],
                    [0.0, 0.0, -1.0, 0.0],
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            )
            self.data["active_depth"] = active_depth.calc_main_depth_from_left_right_ir(
                image_left,
                image_right,
                left_extrinsic_matrix,
                right_extrinsic_matrix,
                main_extrinsic_matrix,
                self.ir_intrinsic_matrix,
                self.ir_intrinsic_matrix,
                self.main_intrinsic_matrix,
                lr_consistency=False,
                main_cam_size=(
                    self.main_intrinsic_matrix[0, 2] * 2,
                    self.main_intrinsic_matrix[1, 2] * 2,
                ),
                ndisp=128,
                use_census=True,
                register_depth=True,
                census_wsize=7,
                use_noise=False,
            )
            self.data["active_depth"][self.data["active_depth"] > 8.0] = 0
            self.data["active_depth"][self.data["active_depth"] < 0.1] = 0

    def GetActiveDepth(
        self,
        main_intrinsic_matrix_local: np.ndarray,
        ir_intrinsic_matrix_local: np.ndarray,
    ):
        """
        Get IR-based depth image.

        :param main_intrinsic_matrix_local: np.ndarray The intrinsic matrix of main camera.
        :param ir_intrinsic_matrix_local: np.ndarray The intrinsic matrix of IR-based camera.
        """
        self.main_intrinsic_matrix = main_intrinsic_matrix_local
        self.ir_intrinsic_matrix = ir_intrinsic_matrix_local
        self._send_data("GetActiveDepth", self.ir_intrinsic_matrix)
