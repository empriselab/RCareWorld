from abc import ABC
import os
import pathlib
from pyrcareworld.objects import RCareWorldBaseObject
from pyrfuniverse.utils.kinova_controller import RFUniverseKinovaController
from pyrfuniverse.utils.stretch_controller import RFUniverseStretchController
from pyrfuniverse.utils.controller import RFUniverseController
from pyrfuniverse.utils.jaco_controller import RFUniverseJacoController
from pyrfuniverse.utils.ur5_controller import RFUniverseUR5Controller
import pyrfuniverse
import pyrfuniverse.utils.rfuniverse_utility as utility

class Robot(RCareWorldBaseObject):
    """
    This class is for robots in RCareWorld, including robot arms and mobile manipulators.
    """
    def __init__(self, env, id:int, gripper_id:list, robot_name:str, urdf_path=None,  base_pose:list = [0,0,0], base_orientation:list = [-0.707107, 0.0, 0.0, -0.707107], is_in_scene:bool = False):
        super().__init__(
            env=env,
            id=id,
            name=robot_name,
            is_in_scene=is_in_scene
        )
        """
        Initialization function.
        @param env: The environment object
        @param id: ID of this robot
        @param gripper_id:  A list of IDs of the grippers. For bimanual manipulator there might be two grippers, so this is a list.
        @param hand_camera: Whether there is a camera on the hand
        """
        self.env = env
        self.robot_id = id
        self.gripper_id = gripper_id
        self.hand_camera = False
        self.is_mobile = False

        self.base_pose = base_pose
        self.base_orientation = base_orientation

        self.robot_name = robot_name
        self.robot_type = robot_name.split('-')[0]

        self.robot_type_dict = {
            'franka': '',
            'kinova_gen3_6dof':'',
            'kinova_gen3_7dof':'kinova_gen3/GEN3_URDF_V12.urdf',
            'jaco_6dof':'',
            'jaco_7dof':'Jaco/j2s7s300_gym.urdf',
            'stretch':'',
            'ur5':'',
        }
        self.urdf_path_prefix = os.path.join(pathlib.Path(__file__).parent.resolve(), 'URDF/')
        if self.robot_type in self.robot_type_dict.keys():
            urdf_path = os.path.join(self.urdf_path_prefix, self.robot_type_dict[self.robot_type])
            robot_prefix= self.robot_type.split('_')[0]
            if robot_prefix == 'kinova':
                self.ik_controller = RFUniverseKinovaController(
                    robot_urdf=urdf_path,
                    base_pos= self.base_pose,
                    base_orn= self.base_orientation
                )
            elif robot_prefix == 'jaco':
                self.ik_controller = RFUniverseJacoController(
                    robot_urdf=urdf_path,
                    base_pos= self.base_pose,
                    base_orn= self.base_orientation
                )
            elif robot_prefix == 'stretch':
                self.ik_controller = RFUniverseStretchController(
                    robot_urdf=urdf_path,
                    base_pos= self.base_pose,
                    base_orn= self.base_orientation
                )
            elif robot_prefix == 'franka':
                self.ik_controller = RFUniverseController(
                    robot_urdf=urdf_path,
                    base_pos= self.base_pose,
                    base_orn= self.base_orientation
                )
            elif robot_prefix == 'ur5':
                self.ik_controller = RFUniverseUR5Controller(
                    robot_urdf=urdf_path,
                    base_pos= self.base_pose,
                    base_orn= self.base_orientation
                )
        elif self.robot_type not in self.robot_type_dict.keys() and self.robot_type is None:
            print("Robot type not available directly. Please make sure the input matches the supported robot types, or load your robot with URDF in Unity editor and specify urdf path")
        else:
            # self.ik_controller = RFUniverseController(
            #     robot_urdf=urdf_path
            # )
            print("BioIK Only")

    def getNumJoints(self) -> int:
        """
        Return number of movable joints
        @return: number of movable joints
        """
        num_joints = self.env.instance_channel.data[self.robot_id]["number_of_moveable_joints"]
        return num_joints

    def getInfoRaw(self) -> dict:
        """
        Return states
        @Cathy: I don't like the keys here!
        @return:
        Keys:
        number_of_joints: int, number of movable joints
        positions: list3 of global position
        rotations: list3 of global rotation, euler angle
        quaternion: list4 of global rotation, quaternion
        Local_positions: list3 of local position
        Local_rotations: list3 of local rotation, euler angle
        Local_quaternion: list4 of local quarternion, quaternion
        velocities: list3 of velocity
        number_of_moveable_joints: int
        joint_positions: list of float, joint positions
        joint_velocities: list of float, joint velocities
        all_stable: bool, whether all parts are stable
        move_done: bool, whether move is finished TODO: check if this is working
        rotate_done: bool, whether rotation is finished TODO: check if this is working
        gravity_forces: list of float
        coriolis_centrifugal_forces: list of float
        drive_forces: list of float
        """
        info =  self.env.instance_channel.data[self.robot_id]
        return info

    def getRawInfoGripper(self):
        """
        Get raw info for gripper.
        @return:
        dict with the same keywords but for the gripper
        """
        info = self.env.instance_channel.data[self.gripper_id]
        return info
    def isMoveDone(self) -> bool:
        """

        @return:
        """
        move_done = not self.env.instance_channel.data[self.robot_id]['all_stable']
        return move_done

    def getInfoParsed(self):
        """

        @return:
        number_of_joints: int, number of joints
        positions: list3 of global position
        rotations: list3 of global rotation, euler angle
        quaternion: list4 of global rotation, quaternion
        Local_positions: list3 of local position
        Local_rotations: list3 of local rotation, euler angle
        Local_quaternion: list4 of local quarternion, quaternion
        velocities: list3 of velocity
        number_of_moveable_joints: int
        joint_positions: list of float, joint rotations
        joint_velocities: list of float, joint velocities
        all_stable: bool, whether all parts are stable
        move_done: bool, whether move is finished TODO: check if this is working
        rotate_done: bool, whether rotation is finished TODO: check if this is working
        gravity_forces: list of float
        coriolis_centrifugal_forces: list of float
        drive_forces: list of float
        """
        info = {}
        raw_info = self.env.instance_channel.data[self.robot_id]
        # print(raw_info)
        # raw_number_of_joints = raw_info["number_of_joints"]
        info["num_joints"] = raw_info["number_of_joints"]
        info["base_pos"] = raw_info["positions"]
        info["base_rot"] = raw_info["rotations"]
        info["base_quat"] = raw_info["quaternion"]
        info["base_local_pos"] = raw_info["Local_positions"]
        info["base_local_rot"] = raw_info["Local_rotations"]
        info["base_local_quat"] = raw_info["Local_quaternion"]
        info["base_vel"] = raw_info["velocities"]
        info["num_joints_movable"] = raw_info["number_of_moveable_joints"]
        info["joint_poses"] = raw_info["joint_positions"]
        info["joint_vels"] = raw_info["joint_velocities"]
        info["all_stable"] = raw_info["all_stable"]
        info["move_done"] = raw_info["move_done"]
        info["rotate_done"] = raw_info["rotate_done"]
        # info["gravity_forces"] = raw_info["gravity_forces"]
        # info["coriolis_centrifugal_forces"] = raw_info["coriolis_centrifugal_forces"]
        # info["drive_forces"] = raw_info["drive_forces"]

        return info

    def getInfoParsedGripper(self):
        """
        Get parsed information but is for gripper
        @return: Dict with the same keywords as getInfoParsed
        """
        info = {}
        raw_info = self.env.instance_channel.data[self.gripper_id]
        # print(raw_info)
        # raw_number_of_joints = raw_info["number_of_joints"]
        info["num_joints"] = raw_info["number_of_joints"]
        info["base_pos"] = raw_info["positions"]
        info["base_rot"] = raw_info["rotations"]
        info["base_quat"] = raw_info["quaternion"]
        info["base_local_pos"] = raw_info["Local_positions"]
        info["base_local_rot"] = raw_info["Local_rotations"]
        info["base_local_quat"] = raw_info["Local_quaternion"]
        info["base_vel"] = raw_info["velocities"]
        info["num_joints_movable"] = raw_info["number_of_moveable_joints"]
        info["joint_poses"] = raw_info["joint_positions"]
        info["joint_vels"] = raw_info["joint_velocities"]
        info["all_stable"] = raw_info["all_stable"]
        info["move_done"] = raw_info["move_done"]
        info["rotate_done"] = raw_info["rotate_done"]
        return info


    def getJointStates(self, joint_id):
        assert joint_id<self.env.instance_channel.data[id]["number_of_moveable_joints"] is True, "Joint ID should be less than the number of movable joints"
        info = {}
        robot_info = self.getInfoParsed()
        info["joint_pose"] = robot_info["joint_poses"][joint_id]
        info["joint_vel"] = robot_info["joint_vels"][joint_id]
        info["joint_force"] = robot_info["drive_forces"][joint_id]
        return info

    def setJointPositions(self, joint_positions:list, speed_scales=None) -> None:
        """
        @param joint_positions: list of joint positions, starting from base, in degree TODO need check
        @param speed_scales: A list inferring each joint's speed scale.
        @return: does not return anything
        """
        if speed_scales is not None:
            self.env.instance_channel.set_action(
                'SetJointPosition',
                id = self.robot_id,
                joint_positions=list(joint_positions),
                speed_scales=list(speed_scales)
            )
        if speed_scales is None:
            self.env.instance_channel.set_action(
                'SetJointPosition',
                id=self.robot_id,
                joint_positions=list(joint_positions),
            )

    def setJointPositionsDirectly(self, joint_positions:list) -> None:
        """
        @param joint_positions: list of joint positions, starting from base, in degree TODO need check
        @return: does not return anything
        """
        self.env.instance_channel.set_action(
            'SetJointPosition',
            id = self.robot_id,
            joint_positions = joint_positions
        )

    def setJointPositionsContinue(self, joint_positions: list, interval:int, time_joint_positions:int)->None:
        """
        @param joint_positions: list of joint positions, starting from base, in degree TODO need check
        @return:
        """
        self.env.instance_channel.set_action(
            'SetJointPositionContinue',
            id=self.robot_id,
            interval = interval,
            time_joint_positions = time_joint_positions
        )

    def setJointVelocities(self, joint_velocities:list)->None:
        """
        @param joint_velocities:
        @return:
        """
        self.env.instance_channel.set_action(
            'SetJointVelocity',
            id = self.robot_id,
            joint_velocitys = joint_velocities
        )

    def setJointForces(self, joint_forces:list)->None:
        """

        @param joint_forces:
        @return:
        """
        self.env.instance_channel.set_action(
            'AddJointForce',
            id = self.robot_id,
            joint_forces = joint_forces
        )

    def setJointTorques(self, joint_torques:list)->None:
        """

        @param joint_torques:
        @return:
        """
        self.env.instance_channel.set_action(
            'AddJointForce',
            id=self.robot_id,
            joint_forces=joint_torques
        )

    def getJointInverseDynamicsForces(self)->dict:
        """

        @return: A dictionary
        Keys: M(q)q_dd + C(q, q_d)q_d + G(q) + J(q)*f_ext = Tau
        drive_forces: Tau
        TODO: add other force items
        """
        joint_dynamics_forces = self.env.instance_channel.set_action(
            'GetJointInverseDynamicsForce',
            id=self.robot_id
        )
        self.env._step()
        info = self.getInfoRaw()
        gravity_forces = info['gravity_forces']
        coriolis_centrifugal_forces = info['coriolis_centrifugal_forces']
        drive_forces = info['drive_forces']

        forces = {}
        forces['gravity_force'] = gravity_forces
        forces['coriolis_force'] = coriolis_centrifugal_forces
        forces['drive_force'] = drive_forces
        return forces

    def setImmovable(self)->None:
        """

        @return:
        """
        self.env.instance_channel.set_action(
            'SetImmovable',
            id = self.robot_id
        )


    def setJointForcesAtPositions(self, joint_forces: list, force_positions: list) -> None:
        """

        @param jiont_forces:
        @param force_positions:
        @return:
        """
        self.env.instance_channel.set_action(
            'AddJointForceAtPosition',
            id=self.robot_id,
            joint_forces = joint_forces,
            forces_position = force_positions
        )


    def moveForward(self, distance: float, speed: float) -> None:
        assert self.is_mobile is True, 'This method is only for mobile manipulators.'
        self.env.instance_channel.set_action(
            'MoveForward',
            id=self.robot_id,
            distance=distance,
            speed=speed
        )

    def moveBackward(self, distance: float, speed: float) -> None:
        assert self.is_mobile is True, 'This method is only for mobile manipulators.'
        self.env.instance_channel.set_action(
            'MoveBack',
            id=self.robot_id,
            distance=distance,
            speed=speed
        )

    def turnLeft(self, angle: float, speed: float) -> None:
        assert self.is_mobile is True, 'This method is only for mobile manipulators.'
        self.env.instance_channel.set_action(
            'TurnLeft',
            id=self.robot_id,
            angle=angle,
            speed=speed
        )

    def turnRight(self, angle: float, speed: float) -> None:
        assert self.is_mobile is True, 'This method is only for mobile manipulators.'
        self.env.instance_channel.set_action(
            'TurnRight',
            id=self.robot_id,
            angle=angle,
            speed=speed
        )

    def moveTo(self, targetPose:list, targetRot = None) -> None:
        if targetRot is not None:
            joint_positions = self.ik_controller.calculate_ik_recursive(targetPose, targetRot)
        else:
            joint_positions = self.ik_controller.calculate_ik_recursive(targetPose)
        self.setJointPositions(joint_positions)
        self.env._step()
        # print(self.isMoveDone())
        # while self.isMoveDone() is False:
        #     self.env._step()

    def directlyMoveTo(self, targetPose:list, targetRot:list = None) -> None:
        if targetRot is not None:
            joint_positions = self.ik_controller.calculate_ik_recursive(targetPose, targetRot)
        else:
            joint_positions = self.ik_controller.calculate_ik_recursive(targetPose)
        self.setJointPositionsDirectly(joint_positions)
        self.env._step()

    def reset(self) -> None:
        self.ik_controller.reset()

    def getGripperPosition(self) -> list:
        if len(self.gripper_id)==1:
            # print(self.env.instance_channel.data[self.gripper_id[0]])
            return self.env.instance_channel.data[self.gripper_id[0]]['position']

    def getGripperVelocity(self) -> list:
        if len(self.gripper_id) == 1:
            return self.env.instance_channel.data[self.gripper_id[0]]['velocities'][0]

    def getJointAccelerations(self) -> list:
        joint_acccelerations = self.env.instance_channel.set_action(
            "GetJointAccelerations",
            id = self.robot_id
        )
        return joint_acccelerations

    def load(self) -> None:
        self.env.asset_channel.set_action(
            'InstanceObject',
            id=self.robot_id,
            name=self.robot_name
        )
        self.env._step()

    def BioIKMove(self, targetPose:list, duration:float, relative:bool) -> None:
        self.env.instance_channel.set_action(
            'IKTargetDoMove',
            id=self.robot_id,
            position=targetPose,
            duration=duration,
            relative=relative
        )
        self.env._step()
        while not self.env.instance_channel.data[self.robot_id]['move_done']:
            self.env._step()

    def BioIKRotateQua(self, taregetEuler:list, duration:float, relative:bool) -> None:
        self.env.instance_channel.set_action(
            'IKTargetDoRotateQuaternion',
            id=self.robot_id,
            quaternion=utility.UnityEularToQuaternion(taregetEuler),
            duration=duration,
            relative=relative
        )
        self.env._step()
        while not self.env.instance_channel.data[self.robot_id]['move_done'] or not self.env.instance_channel.data[self.robot_id]['rotate_done']:
            self.env._step()


if __name__ == '__main__':
    print(os.path.join(pathlib.Path(__file__).parent.resolve(), 'URDF/'))



