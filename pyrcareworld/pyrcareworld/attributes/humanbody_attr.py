import pyrcareworld.attributes as attr


class HumanbodyAttr(attr.BaseAttr):
    """
    Human body Inverse Kinematic class.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by internal function.

        Returns:
            Dict: A dict containing useful information of this class.

            self.data['move_done']: Whether the movement has finished.

            self.data['rotate_done']: Whether the rotation has finished.
        """
        super().parse_message(data)

    def HumanIKTargetDoMove(
        self,
        index: int,
        position: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Human body Inverse Kinematics target movement.

        Args:
            index: Int, the target for movement. 0 for left hand, 1 for right hand,2 for left foot, 3 for right foot, 4 for head.
            position: A list of length 3, representing the position.
            duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
            speed_based: Bool.
            relative: Bool, if True, `position` is relative; otherwise, `position` is absolute.
        """
        if position is not None:
            assert len(position) == 3, "position length must be 3"
            position = [float(i) for i in position]
        self._send_data(
            "HumanIKTargetDoMove",
            index,
            position,
            float(duration),
            speed_based,
            relative,
        )

    def HumanIKTargetDoRotate(
        self,
        index: int,
        rotation: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Human body Inverse Kinematics target rotation.

        Args:
            index: Int, the target for movement. 0 for left hand, 1 for right hand,2 for left foot, 3 for right foot, 4 for head.
            rotation: A list of length 3, representing the rotation.
            duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
            speed_based: Bool.
            relative: Bool, if True, `rotation` is relative; otherwise, `rotation` is absolute.
        """
        if rotation is not None:
            assert len(rotation) == 3, "rotation length must be 3"
            rotation = [float(i) for i in rotation]
        self._send_data(
            "HumanIKTargetDoRotate",
            index,
            rotation,
            float(duration),
            speed_based,
            relative,
        )

    def HumanIKTargetDoRotateQuaternion(
        self,
        index: int,
        quaternion: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Human body Inverse Kinematics target rotation using quaternion.

        Args:
            index: Int, the target for movement. 0 for left hand, 1 for right hand,2 for left foot, 3 for right foot, 4 for head.
            quaternion: A list of length 4, representing the quaternion.
            duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
            speed_based: Bool.
            relative: Bool, if True, `quaternion` is relative; otherwise, `quaternion` is absolute.
        """
        if quaternion is not None:
            assert len(quaternion) == 4, "quaternion length must be 4"
            quaternion = [float(i) for i in quaternion]
        self._send_data(
            "HumanIKTargetDoRotateQuaternion",
            index,
            quaternion,
            float(duration),
            speed_based,
            relative,
        )

    def HumanIKTargetDoComplete(self, index: int):
        """
        Make the human body IK target movement / rotation complete directly.

        Args:
            index: Int, the target for movement. 0 for left hand, 1 for right hand,2 for left foot, 3 for right foot, 4 for head.
        """
        self._send_data("HumanIKTargetDoComplete", index)

    def HumanIKTargetDoKill(self, index: int):
        """
        Make the human body IK target movement / rotation stop.

        Args:
            index: Int, the target for movement. 0 for left hand, 1 for right hand,2 for left foot, 3 for right foot, 4 for head.
        """
        self._send_data("HumanIKTargetDoKill", index)
