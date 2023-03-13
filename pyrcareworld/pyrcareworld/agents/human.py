from abc import ABC

from pyrfuniverse.environment import UnityEnvironment
from pyrfuniverse.side_channel.environment_parameters_channel import EnvironmentParametersChannel
from pyrfuniverse.rfuniverse_channel import AssetChannel
from pyrfuniverse.rfuniverse_channel import InstanceChannel
from pyrfuniverse.rfuniverse_channel import DebugChannel

class Human(ABC):
    """
    Humans in RCareWorld
    """
    def __init__(self, env, id:int, name:str, is_inscene:bool = False):
        self.env = env
        self.id = id
        self.name = name
        self.is_inscene = is_inscene

    def load(self):
        self.env.asset_channel.set_action(
            'InstanceObject',
            id=self.id,
            name=self.name
        )
        self.env._step()
        self.is_inscene = True

    def destroy(self):
        """
        Destroy the object in the scene.
        """
        self.env.instance_channel.set_action(
            'Destroy',
            id=self.id
        )
        self.is_in_scene = False
        self.env._step()

    def setBasePosition(self, position:list):
        self.env.instance_channel.set_action(
            "SetTransform",
            id=self.id,
            position=position
        )

    def setRootRotation(self, rotation:list):
        self.env.instance_channel.set_action(
            "SetTransform",
            id=self.id,
            rotation=rotation
        )

    def setJointPoisitionByName(self, joint_name:str, position:list):
        # bone name list:
        name_list = ['Pelvis', 'Spine1', 'Spine2', 'Spine3', 'LeftShoulder', 'LeftUpperArm', 'LeftLowerArm', 'LeftHand', 'RightShoulder', 'RightUpperArm', 'RightLowerArm', 'RightHand', 'LeftUpperLeg', 'LeftLowerLeg', 'LeftFoot', 'LeftToes', 'RightUpperLeg', 'RightLowerLeg', 'RightFoot', 'RightToes', 'Neck', 'Head', 'LeftEye', 'RightEye', 'Jaw', 'LeftThumb1', 'LeftThumb2', 'LeftThumb3', 'LeftIndex1', 'LeftIndex2', 'LeftIndex3', 'LeftMiddle1', 'LeftMiddle2', 'LeftMiddle3', 'LeftRing1', 'LeftRing2', 'LeftRing3', 'LeftPinky1', 'LeftPinky2', 'LeftPinky3', 'RightThumb1', 'RightThumb2', 'RightThumb3', 'RightIndex1', 'RightIndex2', 'RightIndex3', 'RightMiddle1', 'RightMiddle2', 'RightMiddle3', 'RightRing1', 'RightRing2', 'RightRing3', 'RightPinky1', 'RightPinky2', 'RightPinky3']
        if joint_name not in name_list:
            raise ValueError("The joint name is not in the list")
        self.env.instance_channel.set_action(
            "SetNameBonePosition",
            id=self.id,
            bone_name=joint_name,
            bone_position=position[0],
            bone_position_y = position[1],
            bone_position_z = position[2]
        )

    def setJointPoisitionByNameDirectly(self, joint_name:str, position:list):
        name_list = ['Pelvis', 'Spine1', 'Spine2', 'Spine3', 'LeftShoulder', 'LeftUpperArm', 'LeftLowerArm', 'LeftHand',
                     'RightShoulder', 'RightUpperArm', 'RightLowerArm', 'RightHand', 'LeftUpperLeg', 'LeftLowerLeg',
                     'LeftFoot', 'LeftToes', 'RightUpperLeg', 'RightLowerLeg', 'RightFoot', 'RightToes', 'Neck', 'Head',
                     'LeftEye', 'RightEye', 'Jaw', 'LeftThumb1', 'LeftThumb2', 'LeftThumb3', 'LeftIndex1', 'LeftIndex2',
                     'LeftIndex3', 'LeftMiddle1', 'LeftMiddle2', 'LeftMiddle3', 'LeftRing1', 'LeftRing2', 'LeftRing3',
                     'LeftPinky1', 'LeftPinky2', 'LeftPinky3', 'RightThumb1', 'RightThumb2', 'RightThumb3',
                     'RightIndex1', 'RightIndex2', 'RightIndex3', 'RightMiddle1', 'RightMiddle2', 'RightMiddle3',
                     'RightRing1', 'RightRing2', 'RightRing3', 'RightPinky1', 'RightPinky2', 'RightPinky3']
        if joint_name not in name_list:
            raise ValueError("The joint name is not in the list")
        self.env.instance_channel.set_action(
            "SetNameBonePositionDirectly",
            id=self.id,
            bone_name=joint_name,
            bone_position=position[0],
            bone_position_y=position[1],
            bone_position_z=position[2]
        )

    def getJointStateByName(self, joint_name:str):
        name_list = ['Pelvis', 'Spine1', 'Spine2', 'Spine3', 'LeftShoulder', 'LeftUpperArm', 'LeftLowerArm', 'LeftHand',
                        'RightShoulder', 'RightUpperArm', 'RightLowerArm', 'RightHand', 'LeftUpperLeg', 'LeftLowerLeg',
                        'LeftFoot', 'LeftToes', 'RightUpperLeg', 'RightLowerLeg', 'RightFoot', 'RightToes', 'Neck', 'Head',
                        'LeftEye', 'RightEye', 'Jaw', 'LeftThumb1', 'LeftThumb2', 'LeftThumb3', 'LeftIndex1', 'LeftIndex2',
                        'LeftIndex3', 'LeftMiddle1', 'LeftMiddle2', 'LeftMiddle3', 'LeftRing1', 'LeftRing2', 'LeftRing3',
                        'LeftPinky1', 'LeftPinky2', 'LeftPinky3', 'RightThumb1', 'RightThumb2', 'RightThumb3',
                        'RightIndex1', 'RightIndex2', 'RightIndex3', 'RightMiddle1', 'RightMiddle2', 'RightMiddle3',
                        'RightRing1', 'RightRing2', 'RightRing3', 'RightPinky1', 'RightPinky2', 'RightPinky3']
        if joint_name not in name_list:
            raise ValueError("The joint name is not in the list")
        joint_states = self.env.instance_channel.data[self.id][joint_name]
        return joint_states

    def saveArticulationBoneData(self, path:str):
        self.env.instance_channel.set_action(
            "SaveArticulationBoneData",
            id=self.id,
            path=path
        )