import pyrcareworld.attributes as attr


class ControllerAttr(attr.ColliderAttr):
    """
    Robot controller class, which will control robot arms, hands and embodied robots.

    Messages received from Unity are expected to include the following keys:

        'number_of_joints': The number of joints in an articulation.

        'names': The name of each part in an articulation.

        'types': The joint type of each part in an articulation.

        'positions': The position of each part in an articulation.

        'rotations': The rotation of each part in an articulation.

        'quaternion': The quaternion of each part in an articulation.

        'local_positions': The local position of each part in an articulation.

        'local_rotations': The local rotation of each part in an articulation.

        'local_quaternion': The local quaternion of each part in an articulation.

        'velocities': The velocity of each part in an articulation.

        'angular_velocities': The angular velocity of each part in an articulation.

        'number_of_moveable_joints': The number of moveable joints in an articulation.

        'joint_positions': The joint position of each moveable joint in an articulation.

        'joint_velocities': The joint velocity of each moveable joint in an articulation.

        'joint_accelerations': The joint accelerations of each moveable joint in an articulation.

        'joint_force': The joint force of each moveable joint in an articulation.

        'joint_lower_limit': The joint lower_limit of each moveable joint in an articulation.

        'joint_upper_limit': The joint upper_limit of each moveable joint in an articulation.

        'joint_stiffness': The joint stiffness of each moveable joint in an articulation.

        'joint_damping': The joint damping of each moveable joint in an articulation.

        'move_done': Whether robot arm IK has finished moving.

        'rotate_done': Whether robot arm IK has finished rotating.

        'gravity_forces': Inverse Dynamics force needed to counteract gravity.

        'coriolis_centrifugal_forces': Inverse Dynamics force needed to counteract coriolis centrifugal forces.

        'drive_forces': Inverse Dynamics drive forces.
    """

    def SetJointPosition(self, joint_positions: list):
        """
        Set the joint position for each moveable joint and move with PD control.

        Args:
            joint_positions: A list of float, representing the target joint positions.
        """
        joint_positions = [float(i) for i in joint_positions]
        self._send_data("SetJointPosition", joint_positions)

    def SetJointPositionDirectly(self, joint_positions: list):
        """
        Set the joint position for each moveable joint and move directly.

        Args:
            joint_positions: A list of float, representing the target joint positions.
        """
        joint_positions = [float(i) for i in joint_positions]
        self._send_data("SetJointPositionDirectly", joint_positions)

    def SetIndexJointPosition(self, index: int, joint_position: float):
        """
        Set the target joint position for a given joint and move with PD control.

        Args:
            index: Int, joint index.
            joint_position: Float, the target joint position.
        """
        self._send_data("SetIndexJointPosition", index, float(joint_position))

    def SetIndexJointPositionDirectly(self, index: int, joint_position: float):
        """
        Set the target joint position for a given joint and move directly.

        Args:
            index: Int, joint index.
            joint_position: Float, the target joint position.
        """
        self._send_data("SetIndexJointPositionDirectly", index, float(joint_position))

    def SetJointPositionContinue(self, interval: int, time_joint_positions: list):
        """
        Set the joint position for each moveable joint and move with PD control continuously.

        Args:
            interval: Float, the time interval.
            time_joint_positions: A list of float list, representing the target joint positions at each time step.
        """
        for i in range(len(time_joint_positions)):
            time_joint_positions[i] = [float(j) for j in time_joint_positions[i]]
        self._send_data("SetJointPositionContinue", interval, time_joint_positions)

    def SetJointStiffness(self, joint_stiffness: list):
        """
        Set the joint stiffness for each moveable joint.

        Args:
            joint_stiffness: A list of float, each moveable joint stiffness.
        """
        joint_stiffness = [float(i) for i in joint_stiffness]
        self._send_data("SetJointStiffness", joint_stiffness)

    def SetJointDamping(self, joint_damping: list):
        """
        Set the joint damping for each moveable joint.

        Args:
            joint_damping: A list of float, each moveable joint damping.
        """
        joint_damping = [float(i) for i in joint_damping]
        self._send_data("SetJointDamping", joint_damping)

    def SetJointLimit(self, joint_upper_limit: list, joint_lower_limit: list):
        """
        Set the joint limit for each moveable joint.

        Args:
            joint_upper_limit: A list of float, each moveable joint upper limit.
            joint_lower_limit: A list of float, each moveable joint lower limit.
        """
        joint_upper_limit = [float(i) for i in joint_upper_limit]
        joint_lower_limit = [float(i) for i in joint_lower_limit]
        self._send_data("SetJointLimit", joint_upper_limit, joint_lower_limit)

    def SetJointVelocity(self, joint_velocitys: list):
        """
        Set the joint velocity for each moveable joint.

        Args:
            joint_velocitys: A list of float, representing the target joint velocities.
        """
        joint_velocitys = [float(i) for i in joint_velocitys]
        self._send_data("SetJointVelocity", joint_velocitys)

    def SetIndexJointVelocity(self, index: int, joint_velocity: float):
        """
        Set the target joint velocity for a given joint.

        Args:
            index: Int, joint index.
            joint_velocity: A list of float, representing the target joint velocities.
        """
        self._send_data("SetIndexJointVelocity", index, float(joint_velocity))

    def SetJointUseGravity(self, use_gravity: bool):
        """
        Set the all joint use or non-use gravity.

        Args:
            use_gravity: Bool, use or non-use gravity.
        """
        self._send_data("SetJointUseGravity", use_gravity)

    def SetJointDriveForce(self, joint_drive_forces: list):
        """
        Set the joint drive forces for each moveable joint.

        Args:
            joint_drive_forces: A list of float, representing the joint drive forces.
        """
        joint_drive_forces = [float(i) for i in joint_drive_forces]
        self._send_data('SetJointDriveForce', joint_drive_forces)

    def AddJointForce(self, joint_forces: list):
        """
        Add force to each moveable joint.

        Args:
            joint_forces: A list of forces, representing the added forces.
        """
        joint_forces = [float(i) for i in joint_forces]
        self._send_data("AddJointForce", joint_forces)

    def AddJointForceAtPosition(self, joint_forces: list, force_positions: list):
        """
        Add force to each moveable joint at a given position.

        Args:
            joint_forces: A list of forces, representing the added forces.
            force_positions: A list of positions, representing the positions for forces.
        """
        assert len(joint_forces) == len(force_positions), "The length of joint_forces and force_positions are not equal."
        self._send_data("AddJointForceAtPosition", joint_forces, force_positions)

    def AddJointTorque(self, joint_torques: list):
        """
        Add torque to each moveable joint.

        Args:
            joint_torques: A list of torques, representing the added torques.
        """
        self._send_data("AddJointTorque", joint_torques)

    # only work on unity 2022.1+
    def GetJointInverseDynamicsForce(self):
        """
        Get the joint inverse dynamic force of each moveable joint. Note that this function only works in Unity version >= 2022.1.
        """
        self._send_data("GetJointInverseDynamicsForce")

    def SetImmovable(self, immovable: bool):
        """
        Set whether the base of articulation is immovable.

        Args:
            immovable: Bool, True for immovable, False for movable.
        """
        self._send_data("SetImmovable", immovable)

    def MoveForward(self, distance: float, speed: float):
        """
        Move robot forward. Only works if the robot controller has a mobile platform.
        Args:
            distance: Float, distance.
            speed: Float, velocity.
        """
        self._send_data("MoveForward", float(distance), float(speed))

    def MoveBack(self, distance: float, speed: float):
        """
        Move robot backword. Only works if the robot controller has a mobile platform.

        Args:
            distance: Float, distance.
            speed: Float, velocity.
        """
        self._send_data("MoveBack", float(distance), float(speed))

    def TurnLeft(self, angle: float, speed: float):
        """
        Turn robot left. Only works if the robot controller has a mobile platform.
        Args:
            angle: Float, rotation angle.
            speed: Float, velocity.
        """
        self._send_data("TurnLeft", float(angle), float(speed))

    def TurnRight(self, angle: float, speed: float):
        """
        Turn robot right. Only works if the robot controller has a mobile platform.

        Args:
            angle: Float, rotation angle.
            speed: Float, velocity.
        """
        self._send_data("TurnRight", float(angle), float(speed))

    def GripperOpen(self):
        """
        Open the gripper. 
        """
        self._send_data("GripperOpen")

    def GripperClose(self):
        """
        Close the gripper. 
        """
        self._send_data("GripperClose")

    def EnabledNativeIK(self, enabled: bool):
        """
        Enable or disable the native IK algorithm.

        Args:
            enabled: Bool, True for enable and False for disable.When it is True, through the IKTatGetDo*** interface, according to the end pose.When it is False, through the SetJoint*** interface, according to the joint movement.NativeIK can only take effect when it is started during initialization.
        """
        self._send_data("EnabledNativeIK", enabled)

    def IKTargetDoMove(
        self,
        position: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Native IK target movement.

        Args:
            position: A list of length 3, representing the position.
            duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
            speed_based: Bool.
            relative: Bool, if True, `position` is relative; otherwise, `position` is absolute.
        """
        if position is not None:
            assert len(position) == 3, "position length must be 3"
            position = [float(i) for i in position]

        self._send_data(
            "IKTargetDoMove", position, float(duration), speed_based, relative
        )

    def IKTargetDoRotate(
        self,
        rotation: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Native IK target rotation.

        Args:
            rotation: A list of length 3, representing the rotation.
            duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
            speed_based: Bool.
            relative: Bool, if True, `rotation` is relative; otherwise, `rotation` is absolute.
        """
        if rotation is not None:
            assert len(rotation) == 3, "rotation length must be 3"
            rotation = [float(i) for i in rotation]

        self._send_data(
            "IKTargetDoRotate", rotation, float(duration), speed_based, relative
        )

    def IKTargetDoRotateQuaternion(
        self,
        quaternion: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Native IK target rotation using quaternion.

        Args:
            quaternion: A list of length 4, representing the quaternion.
            duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
            speed_based: Bool.
            relative: Bool, if True, `quaternion` is relative; otherwise, `quaternion` is absolute.
        """
        if quaternion is not None:
            assert len(quaternion) == 4, "quaternion length must be 4"
            quaternion = [float(i) for i in quaternion]

        self._send_data(
            "IKTargetDoRotateQuaternion",
            quaternion,
            float(duration),
            speed_based,
            relative,
        )

    def IKTargetDoComplete(self):
        """
        Make native IK target movement / rotation complete directly.
        """
        self._send_data("IKTargetDoComplete")

    def IKTargetDoKill(self):
        """
        Make native IK target movement / rotation stop.
        """
        self._send_data("IKTargetDoKill")

    def GetIKTargetJointPosition(self, position: list = None, rotation: list = None, quaternion: list = None, iterate: int = 100):
        """
        Input ik target pose and get the IK calculation results, After calling this method and stepping once, the result will be saved in 'result_joint_position'

        Args:
            position: A list of length 3, representing the position of ik target.
            rotation: A list of length 3, representing the euler angle of ik target.
            quaternion: A list of length 4, representing the quaternion of ik target, If this parameter is specified, `rotation` will be ignored.
            iterate: int, IK calculates the number of iterations.
        """
        if position is not None:
            assert len(position) == 3, "position length must be 3"
            position = [float(i) for i in position]
        if rotation is not None:
            assert len(rotation) == 3, "rotation length must be 3"
            rotation = [float(i) for i in rotation]
        if quaternion is not None:
            assert len(quaternion) == 4, "quaternion length must be 4"
            quaternion = [float(i) for i in quaternion]
        self._send_data("GetIKTargetJointPosition", position, rotation, quaternion, int(iterate))

    def SetIKTargetOffset(
        self,
        position: list = None,
        rotation: list = None,
        quaternion: list = None,
    ):
        """
        Set the new IK target by setting offset to the original target of native IK.

        Args:
            position: A list of length 3, representing the position offset to original target.
            rotation: A list of length 3, representing the rotation offset to original target.
            quaternion: A list of length 4, representing the quaternion offset to original target. If this parameter is specified, `rotation` will be ignored.
        """
        if position is not None:
            assert len(position) == 3, "position length must be 3"
            position = [float(i) for i in position]
        if rotation is not None:
            assert len(rotation) == 3, "rotation length must be 3"
            rotation = [float(i) for i in rotation]
        if quaternion is not None:
            assert len(quaternion) == 4, "quaternion length must be 4"
            quaternion = [float(i) for i in quaternion]

        self._send_data("SetIKTargetOffset", position, rotation, quaternion)

    def GetJointLocalPointFromWorld(self, joint_index: int, point: list):
        """
        Transform a point from joint local coordinate to world coordinate. After calling this method and stepping once, the result will be saved in 'result_joint_local_point'

        Args:
            joint_index: index of joint
            point: A list of length 3, representing the position of a point.
        """
        assert len(point) == 3, "point length must be 3"
        point = [float(i) for i in point]

        self._send_data("GetJointLocalPointFromWorld", int(joint_index), point)

    def GetJointWorldPointFromLocal(self, joint_index: int, point: list):
        """
        Transform a point from world coordinate to joint local coordinate. After calling this method and stepping once, the result will be saved in 'result_joint_world_point'

        Args:
            joint_index: index of joint
            point: A list of length 3, representing the position of a point.
        """
        assert len(point) == 3, "point length must be 3"
        point = [float(i) for i in point]

        self._send_data("GetJointWorldPointFromLocal", int(joint_index), point)

    def AddRoot6DOF(self, new_id: int = None):
        """
        Add 6-DOF root joint to articulation body, The articulation body is incapable of non-dynamic motion and requires the addition of a 6-DOF root joint for free motion.
        It must be called when the object is first created.
        """
        if new_id is None:
            new_id = int("1" + str(self.id))
        self._send_data("AddRoot6DOF", new_id)
        self.env.attrs[new_id] = ControllerAttr(self.env, new_id)
        return self.env.attrs[new_id]
