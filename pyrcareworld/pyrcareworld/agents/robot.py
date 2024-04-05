import os
import pathlib
from pyrcareworld.objects import RCareWorldBaseObject
from pyrcareworld.utils.kinova_controller import RCareWorldKinovaController
from pyrcareworld.utils.stretch_controller import RCareWorldStretchController
from pyrcareworld.utils.controller import RCareWorldController
from pyrcareworld.utils.jaco_controller import RCareWorldJacoController
from pyrcareworld.utils.ur5_controller import RCareWorldUR5Controller
import pyrcareworld.utils.utility as utility


class Robot(RCareWorldBaseObject):
    def __init__(
        self,
        env,
        id: int,
        gripper_id: list,
        robot_name: str,
        urdf_path: str = None,
        base_pose: list = [0, 0, 0],
        base_orientation: list = [-0.707107, 0.0, 0.0, -0.707107],
        is_in_scene: bool = False,
    ):
        super().__init__(env=env, id=id, name=robot_name, is_in_scene=is_in_scene)
        """
        Initialization function.
        @param env: The environment object
        @param id: ID of this robot
        @param gripper_id:  A list of IDs of the grippers. For bimanual manipulator there might be two grippers, so this is a list.
        @param hand_camera: Whether there is a camera on the hand
        """
        self.gripper_id = gripper_id
        self.hand_camera = False
        self.is_mobile = False

        self.base_pose = base_pose
        self.base_orientation = base_orientation

        self.robot_name = robot_name
        self.robot_type = robot_name.split("-")[0]

        self.robot_type_dict = {
            "franka": "Franka/panda.urdf",
            "kinova_gen3_6dof": "",
            "kinova_gen3_7dof": "kinova_gen3/GEN3_URDF_V12.urdf",
            "jaco_7dof": "Jaco/j2s7s300_gym.urdf",
            "stretch": "Stretch/stretch_uncalibrated.urdf",
            "ur5": "UR5/ur5_robot.urdf",
        }
        self.urdf_path_prefix = os.path.join(
            pathlib.Path(__file__).parent.resolve(), "URDF/"
        )
        if self.robot_type in self.robot_type_dict.keys():
            urdf_path = os.path.join(
                self.urdf_path_prefix, self.robot_type_dict[self.robot_type]
            )
            robot_prefix = self.robot_type.split("_")[0]
            if robot_prefix == "kinova":
                self.ik_controller = RCareWorldKinovaController(
                    robot_urdf=urdf_path,
                    base_pos=self.base_pose,
                    base_orn=self.base_orientation,
                )
            elif robot_prefix == "jaco":
                self.ik_controller = RCareWorldJacoController(
                    robot_urdf=urdf_path,
                    base_pos=self.base_pose,
                    base_orn=self.base_orientation,
                )
            elif robot_prefix == "stretch":
                self.ik_controller = RCareWorldStretchController(
                    robot_urdf=urdf_path,
                    base_pos=self.base_pose,
                    base_orn=self.base_orientation,
                )
            elif robot_prefix == "franka":
                self.ik_controller = RCareWorldController(
                    robot_urdf=urdf_path,
                    base_pos=self.base_pose,
                    base_orn=self.base_orientation,
                )
            elif robot_prefix == "ur5":
                self.ik_controller = RCareWorldUR5Controller(
                    robot_urdf=urdf_path,
                    base_pos=self.base_pose,
                    base_orn=self.base_orientation,
                )
        elif (
            self.robot_type not in self.robot_type_dict.keys()
            and self.robot_type is None
        ):
            print(
                "Robot type not available directly. Please make sure the input matches the supported robot types, or load your robot with URDF in Unity editor and specify urdf path"
            )
        else:
            # self.ik_controller = RCareWorldController(
            #     robot_urdf=urdf_path
            # )
            print("BioIK Only")

    def getInfo(self):
        """
        Get the information of this robot.
        @return: A dictionary containing the information of this robot
        """
        return {"id": self.id, "name": self.robot_name, "gripper_id": self.gripper_id}

    def getNumJoints(self):
        """
        Return number of movable joints
        @return: number of movable joints
        """
        num_joints = self.env.instance_channel.data[self.id]["number_of_movable_joints"]
        return num_joints

    def getRobotState(self) -> dict:
        """
        Returns a dictionary containing detailed information about the robot's current status.
        The information includes:
        - Robot name
        - Position, rotation, and quaternion for both global and local frames
        - Local to world transformation matrix
        - Number of joints and their respective positions and rotations
        - Local positions and rotations of the joints
        - Velocities of the joints and robot
        - Joint positions and velocities for the movablejoints
        - Stability and movement status of the robot

        Returns:
            dict: A dictionary containing the robot's current status, with keys such as 'name',
                  'position', 'rotation', 'quaternion', 'local_position', 'local_rotation',
                  'local_quaternion', 'local_to_world_matrix', 'number_of_joints', 'positions',
                  'rotations', 'local_positions', 'local_rotations', 'velocities',
                  'number_of_movable_joints', 'joint_positions', 'joint_velocities',
                  'all_stable', 'move_done', 'rotate_done'.
        """
        info = self.env.instance_channel.data[self.id]
        return info

    def getJointStates(self, joint_id: int) -> dict:
        """
        Returns a dictionary containing detailed information about the robot's current status.
        The information includes:
        - Joint position
        - Joint velocity
        - Joint force

        Args:
            joint_id (int): The ID of the joint to get the state of.

        Returns:
            dict: A dictionary containing the joint's current status, with keys such as 'joint_position',
                    'joint_velocity', 'joint_force'.
        """
        assert (
            joint_id
            < self.env.instance_channel.data[id]["number_of_movable_joints"]
            is True
        ), "Joint ID should be less than the number of movable joints"
        info = {}
        robot_info = self.getRobotState()
        info["joint_positions"] = robot_info["joint_positions"][joint_id]
        info["joint_velocity"] = robot_info["joint_velocities"][joint_id]
        if "drive_forces" in robot_info.keys():
            info["joint_forces"] = robot_info["drive_forces"][joint_id]
        return info

    def getJointPositions(self) -> list:
        """
        Returns a list containing the positions of all the joints.

        Returns:
            list: A list containing the positions of all the joints.
        """
        robot_info = self.getRobotState()
        return robot_info["joint_positions"]

    def getJointVelocities(self) -> list:
        """
        Returns a list containing the velocities of all the joints.

        Returns:
            list: A list containing the velocities of all the joints.
        """
        robot_info = self.getRobotState()
        return robot_info["joint_velocities"]

    def getJointForces(self):
        """
        Returns a list containing the forces of all the joints.

        Returns:
            list: A list containing the forces of all the joints.
        """
        joint_dynamics_forces = self.env.instance_channel.set_action(
            "GetJointInverseDynamicsForce", id=self.id
        )
        robot_info = self.getRobotState()
        return (
            robot_info["drive_forces"],
            robot_info["gravity_forces"],
            robot_info["coriolis_centrifugal_forces"],
        )

    def getJointAccelerations(self):
        """
        Returns a list containing the accelerations of all the joints.

        Returns:
            list: A list containing the accelerations of all the joints.
        """
        joint_acccelerations = self.env.instance_channel.set_action(
            "GetJointAccelerations", id=self.id
        )
        return joint_acccelerations

    def getJointPositionByID(self, joint_id: int) -> float:
        """
        Returns the current position of the joint.

        Args:
            joint_id (int): The ID of the joint to get the position of.

        Returns:
            float: The position of the joint.
        """
        assert (
            joint_id
            < self.env.instance_channel.data[self.id]["number_of_movable_joints"]
            is True
        ), "Joint ID should be less than the number of movable joints"
        robot_info = self.getRobotState()
        return robot_info["joint_positions"][joint_id]

    def getJointVelocityByID(self, joint_id: int) -> float:
        """
        Returns the current velocity of the joint.

        Args:
            joint_id (int): The ID of the joint to get the velocity of.

        Returns:
            float: The velocity of the joint.
        """
        assert (
            joint_id
            < self.env.instance_channel.data[self.id]["number_of_movable_joints"]
            is True
        ), "Joint ID should be less than the number of movable joints"
        robot_info = self.getRobotState()
        return robot_info["joint_velocities"][joint_id]

    def getJointForceByID(self, joint_id: int):
        """
        Returns the current force of the joint.

        Args:
            joint_id (int): The ID of the joint to get the force of.

        Returns:
            float: The force of the joint.
        """
        print("Joint ID {}".format(joint_id))
        print(
            "Number of movable joints: {}".format(
                self.env.instance_channel.data[self.id]["number_of_movable_joints"]
            )
        )
        assert int(joint_id) < int(
            self.env.instance_channel.data[self.id]["number_of_movable_joints"]
        ), "Joint ID should be less than the number of movable joints"
        joint_dynamics_forces = self.env.instance_channel.set_action(
            "GetJointInverseDynamicsForce", id=self.id
        )

        robot_info = self.getRobotState()

        return (
            robot_info["drive_forces"][joint_id],
            robot_info["gravity_forces"][joint_id],
            robot_info["coriolis_centrifugal_forces"][joint_id],
        )

    def getJointAccelerationByID(self, joint_id: int):
        """
        Returns the current acceleration of the joint.

        Args:
            joint_id (int): The ID of the joint to get the acceleration of.

        Returns:
            float: The acceleration of the joint.
        """
        assert (
            joint_id
            < self.env.instance_channel.data[self.id]["number_of_movable_joints"]
            is True
        ), "Joint ID should be less than the number of movable joints"

        joint_acccelerations = self.env.instance_channel.set_action(
            "GetJointAccelerations", id=self.id
        )
        return joint_acccelerations[joint_id]

    def getGripperPosition(self) -> list:
        """
        Returns the current position of the gripper.

        Returns:
            list: The position of the gripper.
        """
        if len(self.gripper_id) == 1:
            # print(self.env.instance_channel.data[self.gripper_id[0]])
            return self.env.instance_channel.data[self.gripper_id[0]]["position"]

    def getGripperRotation(self) -> list:
        """
        Returns the current rotation of the gripper.

        Returns:
            list: The rotation of the gripper.
        """
        if len(self.gripper_id) == 1:
            return self.env.instance_channel.data[self.gripper_id[0]]["rotation"]

    def getGripperVelocity(self) -> list:
        """
        Returns the current velocity of the gripper.

        Returns:
            list: The velocity of the gripper.
        """
        if len(self.gripper_id) == 1:
            return self.env.instance_channel.data[self.gripper_id[0]]["velocities"][0]

    def getGripperGraspPointPosition(self) -> list:
        """
        Returns the current position of the gripper grasp point.
        """
        if len(self.gripper_id) == 1:
            gripper_data = self.env.instance_channel.data[self.gripper_id[0]]
            positions = gripper_data["positions"]
            grasp_point_position = positions[-1]
            return grasp_point_position

    def setJointPositions(self, joint_positions: list, speed_scales=None) -> None:
        """
        @param joint_positions: list of joint positions, starting from base, in degree TODO need check
        @param speed_scales: A list inferring each joint's speed scale.
        @return: does not return anything
        """
        if speed_scales is not None:
            self.env.instance_channel.set_action(
                "SetJointPosition",
                id=self.id,
                joint_positions=list(joint_positions),
                speed_scales=list(speed_scales),
            )
        if speed_scales is None:
            self.env.instance_channel.set_action(
                "SetJointPosition",
                id=self.id,
                joint_positions=list(joint_positions),
            )

    def setJointPositionsDirectly(self, joint_positions: list) -> None:
        """
        @param joint_positions: list of joint positions, starting from base, in degree TODO need check
        @return: does not return anything
        """
        self.env.instance_channel.set_action(
            "SetJointPositionDirectly", id=self.id, joint_positions=joint_positions
        )

    def setJointPositionsContinue(
        self, joint_positions: list, interval: int, time_joint_positions: int
    ) -> None:
        """
        @param joint_positions: list of joint positions, starting from base, in degree TODO need check
        @return:
        """
        self.env.instance_channel.set_action(
            "SetJointPositionContinue",
            id=self.id,
            interval=interval,
            time_joint_positions=time_joint_positions,
        )

    def setJointForces(self, joint_forces: list) -> None:
        """

        @param joint_forces:
        @return:
        """
        self.env.instance_channel.set_action(
            "AddJointForce", id=self.id, joint_forces=joint_forces
        )

    def setJointTorques(self, joint_torques: list) -> None:
        """

        @param joint_torques:
        @return:
        """
        self.env.instance_channel.set_action(
            "AddJointTorque", id=self.id, joint_torques=joint_torques
        )

    def setJointForcesAtPositions(
        self, joint_forces: list, force_positions: list
    ) -> None:
        """

        @param jiont_forces:
        @param force_positions:
        @return:
        """
        self.env.instance_channel.set_action(
            "AddJointForceAtPosition",
            id=self.id,
            joint_forces=joint_forces,
            forces_position=force_positions,
        )

    def setImmovable(self) -> None:
        """

        @return:
        """
        self.env.instance_channel.set_action("SetImmovable", id=self.id)

    def moveTo(self, targetPose: list, targetRot=None) -> None:
        if targetRot != None:
            joint_positions = self.ik_controller.calculate_ik_recursive(
                targetPose, targetRot
            )
        else:
            joint_positions = self.ik_controller.calculate_ik_recursive(targetPose)
        self.setJointPositions(joint_positions)

    def directlyMoveTo(self, targetPose: list, targetRot: list = None) -> None:
        if targetRot is not None:
            joint_positions = self.ik_controller.calculate_ik_recursive(
                targetPose, targetRot
            )
        else:
            joint_positions = self.ik_controller.calculate_ik_recursive(targetPose)
        self.setJointPositionsDirectly(joint_positions)

    def SetBioIKTargetOffset(self, IKTargetOffset: list) -> None:
        pass

    def BioIKMove(self, targetPose: list, duration: float, relative: bool) -> None:
        self.env.instance_channel.set_action(
            "IKTargetDoMove",
            id=self.id,
            position=targetPose,
            duration=duration,
            relative=relative,
        )
        while not self.env.instance_channel.data[self.id]["move_done"]:
            self.env._step()

    def BioIKRotateQua(
        self, taregetEuler: list, duration: float, relative: bool
    ) -> None:
        self.env.instance_channel.set_action(
            "IKTargetDoRotateQuaternion",
            id=self.id,
            quaternion=utility.UnityEularToQuaternion(taregetEuler),
            duration=duration,
            relative=relative,
        )
        while (
            not self.env.instance_channel.data[self.id]["move_done"]
            or not self.env.instance_channel.data[self.id]["rotate_done"]
        ):
            self.env._step()

    def GripperOpen(self) -> None:
        self.env.instance_channel.set_action("GripperOpen", id=self.gripper_id[0])

    def GripperClose(self) -> None:
        self.env.instance_channel.set_action("GripperClose", id=self.gripper_id[0])

    def reset(self) -> None:
        self.ik_controller.reset()
