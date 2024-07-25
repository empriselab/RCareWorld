import numpy as np


class CoordinateSystemConverter():
    """
    Coordinate System Converter class.

    Args:
        cs1_direction: list, The visual direction corresponding to the xyz axis,
                        can be:
                        ["left"/"right"/"up"/"down"/"forward"/"back"/
                        "l"/"r"/"u"/"d"/"f"/"b"/
                        "-left"/"-right"/"-up"/"-down"/"-forward"/"-back"/
                        "-l"/"-r"/"-u"/"-d"/"-f"/"-b"]
        cs2_direction: list, The visual direction corresponding to the xyz axis,
                        can be:
                        ["left"/"right"/"up"/"down"/"forward"/"back"/
                        "l"/"r"/"u"/"d"/"f"/"b"/
                        "-left"/"-right"/"-up"/"-down"/"-forward"/"-back"/
                        "-l"/"-r"/"-u"/"-d"/"-f"/"-b"]
    """
    def __init__(self, cs1_direction=["right", "up", "forward"], cs2_direction=["right", "up", "forward"]):
        self.cs1_dir, self.cs1_axis, self.cs1_sign, self.cs1_system = self._preprocessing(cs1_direction)
        self.cs2_dir, self.cs2_axis, self.cs2_sign, self.cs2_system = self._preprocessing(cs2_direction)

        self.cs1_to_cs2_map = [
            self.cs1_axis[self.cs2_dir[0]],
            self.cs1_axis[self.cs2_dir[1]],
            self.cs1_axis[self.cs2_dir[2]],
        ]
        self.cs1_to_cs2_sign = [
            self.cs1_sign[self.cs2_dir[0]] * self.cs2_sign[self.cs2_dir[0]],
            self.cs1_sign[self.cs2_dir[1]] * self.cs2_sign[self.cs2_dir[1]],
            self.cs1_sign[self.cs2_dir[2]] * self.cs2_sign[self.cs2_dir[2]],
        ]
        self.cs2_to_cs1_map = [
            self.cs2_axis[self.cs1_dir[0]],
            self.cs2_axis[self.cs1_dir[1]],
            self.cs2_axis[self.cs1_dir[2]],
        ]
        self.cs2_to_cs1_sign = [
            self.cs1_sign[self.cs1_dir[0]] * self.cs2_sign[self.cs1_dir[0]],
            self.cs1_sign[self.cs1_dir[1]] * self.cs2_sign[self.cs1_dir[1]],
            self.cs1_sign[self.cs1_dir[2]] * self.cs2_sign[self.cs1_dir[2]],
        ]
        self.cs1_left_or_right = self.cs1_sign['right'] * self.cs1_sign['up'] * self.cs1_sign['forward']
        self.cs2_left_or_right = self.cs2_sign['right'] * self.cs2_sign['up'] * self.cs2_sign['forward']

    def _preprocessing(self, direction):
        dir = ["", "", ""]
        axis = {}
        sign = {}
        direction_in_left = [[], [], []]
        for i in range(3):
            if direction[i] in ["right", "r", "-l", "-left"]:
                dir[i] = "right"
                axis["right"] = i
                sign["right"] = 1
                direction_in_left[i] = [1, 0, 0]
            elif direction[i] in ["up",  "u",  "-d",  "-down"]:
                dir[i] = "up"
                axis["up"] = i
                sign["up"] = 1
                direction_in_left[i] = [0, 1, 0]
            elif direction[i] in ["forward",  "f",  "-b",  "-back"]:
                dir[i] = "forward"
                axis["forward"] = i
                sign["forward"] = 1
                direction_in_left[i] = [0, 0, 1]
            elif direction[i] in ["-right",  "-r",  "l",  "left"]:
                dir[i] = "right"
                axis["right"] = i
                sign["right"] = -1
                direction_in_left[i] = [-1, 0, 0]
            elif direction[i] in ["-up",  "-u",  "d",  "down"]:
                dir[i] = "up"
                axis["up"] = i
                sign["up"] = -1
                direction_in_left[i] = [0, -1, 0]
            elif direction[i] in ["-forward",  "-f",  "b",  "back"]:
                dir[i] = "forward"
                axis["forward"] = i
                sign["forward"] = -1
                direction_in_left[i] = [0, 0, -1]
            else:
                raise f"{direction[i]} is Unrecognized axis"

        z = self._cross(direction_in_left[0], direction_in_left[1])
        if z == direction_in_left[2]:
            system = 1
        else:
            system = -1
        return dir, axis, sign, system

    def _cross(self, lhs: list, rhs: list) -> list:
        return [lhs[1] * rhs[2] - lhs[2] * rhs[1], lhs[2] * rhs[0] - lhs[0] * rhs[2], lhs[0] * rhs[1] - lhs[1] * rhs[0]]

    def cs1_pos_to_cs2_pos(self, pos: list) -> list:
        """
        Convert position form Coordinate System 1 to Coordinate System 2.

        Args:
            pos: List of length 3, position of Coordinate System 1.

        Return:
            list: List of length 3, position of Coordinate System 2.
        """
        x = pos[self.cs1_to_cs2_map[0]] * self.cs1_to_cs2_sign[0]
        y = pos[self.cs1_to_cs2_map[1]] * self.cs1_to_cs2_sign[1]
        z = pos[self.cs1_to_cs2_map[2]] * self.cs1_to_cs2_sign[2]
        return [x, y, z]

    def cs2_pos_to_cs1_pos(self, pos: list) -> list:
        """
        Convert position form Coordinate System 2 to Coordinate System 1.

        Args:
            pos: List of length 3, position of Coordinate System 2.

        Return:
            list: List of length 3, position of Coordinate System 1.
        """
        x = pos[self.cs2_to_cs1_map[0]] * self.cs2_to_cs1_sign[0]
        y = pos[self.cs2_to_cs1_map[1]] * self.cs2_to_cs1_sign[1]
        z = pos[self.cs2_to_cs1_map[2]] * self.cs2_to_cs1_sign[2]
        return [x, y, z]

    def cs1_quat_to_cs2_quat(self, quat: list) -> list:
        """
        Convert quaternion form Coordinate System 1 to Coordinate System 2.

        Args:
            quat: List of length 3, quaternion of Coordinate System 1.

        Return:
            list: List of length 3, quaternion of Coordinate System 2.
        """
        x = quat[self.cs1_to_cs2_map[0]] * self.cs1_to_cs2_sign[0]
        y = quat[self.cs1_to_cs2_map[1]] * self.cs1_to_cs2_sign[1]
        z = quat[self.cs1_to_cs2_map[2]] * self.cs1_to_cs2_sign[2]
        w = quat[3] * self.cs1_system * self.cs2_system
        return [x, y, z, w]

    def cs2_quat_to_cs1_quat(self, quat: list) -> list:
        """
        Convert quaternion form Coordinate System 2 to Coordinate System 1.

        Args:
            quat: List of length 4, quaternion[x,y,z,w] of Coordinate System 2.

        Return:
            list: List of length 4, quaternion[x,y,z,w] of Coordinate System 1.
        """
        x = quat[self.cs2_to_cs1_map[0]] * self.cs2_to_cs1_sign[0]
        y = quat[self.cs2_to_cs1_map[1]] * self.cs2_to_cs1_sign[1]
        z = quat[self.cs2_to_cs1_map[2]] * self.cs2_to_cs1_sign[2]
        w = quat[3] * self.cs1_system * self.cs2_system
        return [x, y, z, w]

    def cs1_scale_to_cs2_scale(self, scale: list) -> list:
        """
        Convert scale form Coordinate System 1 to Coordinate System 2.

        Args:
            scale: List of length 3, scale of Coordinate System 1.

        Return:
            list: List of length 3, scale of Coordinate System 2.
        """
        x = scale[self.cs1_to_cs2_map[0]]
        y = scale[self.cs1_to_cs2_map[1]]
        z = scale[self.cs1_to_cs2_map[2]]
        return [x, y, z]

    def cs2_scale_to_cs1_scale(self, scale: list) -> list:
        """
        Convert scale form Coordinate System 2 to Coordinate System 1.

        Args:
            scale: List of length 3, scale of Coordinate System 2.

        Return:
            list: List of length 3, scale of Coordinate System 1.
        """
        x = scale[self.cs2_to_cs1_map[0]]
        y = scale[self.cs2_to_cs1_map[1]]
        z = scale[self.cs2_to_cs1_map[2]]
        return [x, y, z]

    def cs1_matrix_to_cs2_matrix(self, matrix) -> np.ndarray:
        """
        Convert rotation matrix form Coordinate System 1 to Coordinate System 2.

        Args:
            matrix: list or np.ndarray shape[3,3], rotation matrix of Coordinate System 1.

        Return:
            np.ndarray: shape[3,3], rotation matrix of Coordinate System 2.
        """
        quaternion = self.matrix_to_quat(matrix)
        quaternion = self.cs1_quat_to_cs2_quat(quaternion)
        return self.quat_to_matrix(quaternion)

    def cs2_matrix_to_cs1_matrix(self, matrix) -> np.ndarray:
        """
        Convert rotation matrix form Coordinate System 2 to Coordinate System 1.

        Args:
            matrix: list or np.ndarray shape[3,3], rotation matrix of Coordinate System 2.

        Return:
            np.ndarray: shape[3,3], rotation matrix of Coordinate System 1.
        """
        quaternion = self.matrix_to_quat(matrix)
        quaternion = self.cs2_quat_to_cs1_quat(quaternion)
        return self.quat_to_matrix(quaternion)

    def quat_to_matrix(self, quat=[0,0,0,1]) -> np.ndarray:
        return np.array([
            [1 - 2 * (quat[1] ** 2 + quat[2] ** 2), 2 * (quat[0] * quat[1] - quat[2] * quat[3]), 2 * (quat[0] * quat[2] + quat[1] * quat[3])],
            [2 * (quat[0] * quat[1] + quat[2] * quat[3]), 1 - 2 * (quat[0] ** 2 + quat[2] ** 2), 2 * (quat[1] * quat[2] - quat[0] * quat[3])],
            [2 * (quat[0] * quat[2] - quat[1] * quat[3]), 2 * (quat[1] * quat[2] + quat[0] * quat[3]), 1 - 2 * (quat[0] ** 2 + quat[1] ** 2)]
        ])

    def matrix_to_quat(self, matrix) -> list:
        m = np.array(matrix, dtype=float)
        trace = np.trace(m)
        if trace > 0:
            s = 0.5 / np.sqrt(trace + 1.0)
            w = 0.25 / s
            x = (m[2, 1] - m[1, 2]) * s
            y = (m[0, 2] - m[2, 0]) * s
            z = (m[1, 0] - m[0, 1]) * s
        elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
            s = 2.0 * np.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2])
            w = (m[2, 1] - m[1, 2]) / s
            x = 0.25 * s
            y = (m[0, 1] + m[1, 0]) / s
            z = (m[0, 2] + m[2, 0]) / s
        elif m[1, 1] > m[2, 2]:
            s = 2.0 * np.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2])
            w = (m[0, 2] - m[2, 0]) / s
            x = (m[0, 1] + m[1, 0]) / s
            y = 0.25 * s
            z = (m[1, 2] + m[2, 1]) / s
        else:
            s = 2.0 * np.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1])
            w = (m[1, 0] - m[0, 1]) / s
            x = (m[0, 2] + m[2, 0]) / s
            y = (m[1, 2] + m[2, 1]) / s
            z = 0.25 * s
        return [x, y, z, w]