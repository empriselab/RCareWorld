from pyrcareworld.envs import RCareWorld
import numpy as np
import pybullet as p
import math


class DressingEnv(RCareWorld):

    # object for cloth
    def __init__(
        self,
        executable_file: str = None,
        scene_file: str = None,
        custom_channels: list = [],
        assets: list = [],
        **kwargs
    ):
        RCareWorld.__init__(
            self,
            executable_file=executable_file,
            scene_file=scene_file,
            custom_channels=custom_channels,
            assets=assets,
            **kwargs,
        )

        # create scene objects here as class variables
        self.robot_id = 639787
        self.robot_dof = 7
        self.bed = self.create_bed(
            id=234567,
            name="BedActuation",
            is_in_scene=True,
        )
        robot = self.create_robot(
            id=self.robot_id,
            gripper_list=["6397870"],
            robot_name="franka_panda",
            base_pos=[0, 0, 1],
        )

    def get_state(self):
        return self.robot.getRobotState()

    def get_robot_joint_positions(self):
        return self.instance_channel.data[self.robot_id]["joint_positions"]

    def get_robot_joint_velocities(self):
        return self.instance_channel.data[self.robot_id]["joint_velocities"]

    def get_robot_joint_accelerations(self):
        return self.instance_channel.data[self.robot_id]["joint_accelerations"]

    def set_robot_joint_position(
        self, joint_positions=None, joint_velocities=None, joint_accelerations=None
    ):

        if joint_positions is not None:
            self.instance_channel.set_action(
                "SetJointPositionDirectly",
                id=self.robot_id,
                joint_positions=list(joint_positions[0 : self.robot_dof]),
            )

        if joint_velocities is not None:
            self.instance_channel.set_action(
                "SetJointVelocity",
                id=self.robot_id,
                joint_velocitys=list(joint_velocities[0 : self.robot_dof]),
            )

        if joint_accelerations is not None:
            self.instance_channel.set_action(
                "SetJointAcceleration",
                id=self.robot_id,
                joint_accelerations=list(joint_accelerations[0 : self.robot_dof]),
            )

    def set_bed_angle(self, angle, duration=25):
        self.bed.setActuationAngle(angle, duration)

    def get_bed_angle(self):
        return self.bed.getCurrentAngle()

    def step(self):
        self._step()
