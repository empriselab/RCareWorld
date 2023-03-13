from abc import ABC

from pyrfuniverse.environment import UnityEnvironment
from pyrfuniverse.side_channel.environment_parameters_channel import EnvironmentParametersChannel
from pyrfuniverse.rfuniverse_channel import AssetChannel
from pyrfuniverse.rfuniverse_channel import InstanceChannel
from pyrfuniverse.rfuniverse_channel import DebugChannel

class Device(ABC):
    """
    This class is for active assistive devices in RCareWorld.
    """
    def __init__(self, env, id:int, name:str):
        self.env = env
        self.id = id
        self.device_name = name

    def getNumJoints(self):
        num_joints = self.env.instance_channel.data[id]["number_of_joints"]
        return num_joints

    def getDeviceInfo(self):
        return self.env.instance_channel.data[self.id]

    def setJointPositions(self, joint_positions:list, speed_scales=None) -> None:
        """
        @param joint_positions: list of joint positions, starting from base, in degree TODO need check
        @param speed_scales: A list inferring each joint's speed scale.
        @return: does not return anything
        """
        if speed_scales is not None:
            self.env.instance_channel.set_action(
                'SetJointPosition',
                id = self.id,
                joint_positions=list(joint_positions),
                speed_scales=list(speed_scales)
            )
        if speed_scales is None:
            self.env.instance_channel.set_action(
                'SetJointPosition',
                id=self.id,
                joint_positions=list(joint_positions),
            )

    def setJointPositionsDirectly(self, joint_positions:list) -> None:
        """
        @param joint_positions: list of joint positions, starting from base, in degree TODO need check
        @return: does not return anything
        """
        self.env.instance_channel.set_action(
            'SetJointPosition',
            id = self.id
        )


    def setJointVelocities(self, joint_velocities:list)->None:
        """
        @param joint_velocities:
        @return:
        """
        self.env.instance_channel.set_action(
            'SetJointVelocity',
            id = self.id,
            joint_velocitys = joint_velocities
        )


    def setImmovable(self)->None:
        """

        @return:
        """
        self.env.instance_channel.set_action(
            'SetImmovable',
            id = self.id
        )

