from pyrcareworld.objects import RCareWorldBaseObject
from typing import Optional


class Human(RCareWorldBaseObject):
    """
    Humans in RCareWorld
    """

    def __init__(self, env, id: int, name: str, is_in_scene: bool = False):
        super().__init__(env=env, id=id, name=name, is_in_scene=is_in_scene)
        self.name_list = [
            "Pelvis",
            "Spine1",
            "Spine2",
            "Spine3",
            "LeftShoulder",
            "LeftUpperArm",
            "LeftLowerArm",
            "LeftHand",
            "RightShoulder",
            "RightUpperArm",
            "RightLowerArm",
            "RightHand",
            "LeftUpperLeg",
            "LeftLowerLeg",
            "LeftFoot",
            "LeftToes",
            "RightUpperLeg",
            "RightLowerLeg",
            "RightFoot",
            "RightToes",
            "Neck",
            "Head",
            "LeftEye",
            "RightEye",
            "Jaw",
            "LeftThumb1",
            "LeftThumb2",
            "LeftThumb3",
            "LeftIndex1",
            "LeftIndex2",
            "LeftIndex3",
            "LeftMiddle1",
            "LeftMiddle2",
            "LeftMiddle3",
            "LeftRing1",
            "LeftRing2",
            "LeftRing3",
            "LeftPinky1",
            "LeftPinky2",
            "LeftPinky3",
            "RightThumb1",
            "RightThumb2",
            "RightThumb3",
            "RightIndex1",
            "RightIndex2",
            "RightIndex3",
            "RightMiddle1",
            "RightMiddle2",
            "RightMiddle3",
            "RightRing1",
            "RightRing2",
            "RightRing3",
            "RightPinky1",
            "RightPinky2",
            "RightPinky3",
        ]

    def setBasePosition(self, position: list):
        """
        Sets the base position for this human object in Unity

        Args:
            position: A list of floats representing the position coordinates for the object, in the form [x, y, z]

        Returns: does not return anything
        """
        self.env.instance_channel.set_action(
            "SetTransform", id=self.id, position=position
        )


    def setRootRotation(self, rotation: list):
        """
        Sets the root rotation for this human object in Unity

        Args:
           rotation: A list of floats [x, y, z] representing the Euler angles for the new rotation coordinates for the human object in degrees

        Returns: does not return anything
        """
        self.env.instance_channel.set_action(
            "SetTransform", id=self.id, rotation=rotation
        )

    def setJointRotationByName(self, joint_name: str, position: list):
        """
        Sets a specified joint on the human object to a certain rotation. Raises a ValueError if the joint is not recognized.

        Args:
        joint_name: a string representing a joint that is to be rotated. Must be in name_list.
        position: a list of floats in the form of [x, y, z] which represent a certain orientation as Euler's angles in degrees.

        Returns: does not return anything
        """
        if joint_name not in self.name_list:
            raise ValueError("The joint name is not in the list")
        self.env.instance_channel.set_action(
            "SetNameBonePosition",
            id=self.id,
            bone_name=joint_name,
            bone_position=position[0],
            bone_position_y=position[1],
            bone_position_z=position[2],
        )


    def setJointLimits(
        self,
        joint_name: str,
        lower_limit: float,
        upper_limit: float,
        axis: Optional[str] = None,
    ):
        """
        Sets the joint limits for this human object in Unity.

        Args:
            joint_name: The name of the joint (or bone).
            lower_limit: The lower limit of the joint.
            upper_limit: The upper limit of the joint.
            axis: The axis of the joint. If None, all axes are set.
        """
        if joint_name not in self.name_list:
            raise ValueError("The joint name is not in the list")

        if (axis in ["X", "Y", "Z"]) is False:
            self.env.instance_channel.set_action(
                "SetJointLimits",
                id=self.id,
                bone_name=joint_name,
                lower_limit=lower_limit,
                upper_limit=upper_limit,
            )
        else:
            self.env.instance_channel.set_action(
                "SetJointLimits",
                id=self.id,
                bone_name=joint_name,
                lower_limit=lower_limit,
                upper_limit=upper_limit,
                axis=axis,
            )

    def setJointRotationByNameDirectly(self, joint_name: str, position: list):
        """
        Sets a joint on the human object to a certain rotational orientation

        Args:
        joint_name: The name of the joint (or bone).
        position: The desired rotational position of the joint

        Returns: does not return anything
        """

        if joint_name not in self.name_list:
            raise ValueError("The joint name is not in the list")
        self.env.instance_channel.set_action(
            "SetNameBonePositionDirectly",
            id=self.id,
            bone_name=joint_name,
            bone_position=position[0],
            bone_position_y=position[1],
            bone_position_z=position[2],
        )

    def getJointStateByName(self, joint_name: str):
        """
        Returns the current state of a joint when given the name of the joint

        Args:
        joint_name: The name of the joint (or bone)

        Returns: the joint's state
        """
        if joint_name not in self.name_list:
            raise ValueError("The joint name is not in the list")
        joint_states = self.env.instance_channel.data[self.id][joint_name]
        return joint_states

    def getJointPositionByName(self, joint_name: str):
        """
        Returns the position of the joint in the world coordinate when given the name of the joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The position of the joint
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["position"]

    def getJointGlobalRotationByName(self, joint_name: str):
        """
        Returns the rotational orientation of the joint as Euler angles in degrees when given the name of the joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The rotational position of the joint as Euler angles in degrees
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["rotation"]

    def getJointQuaternionByName(self, joint_name: str):
        """
        Returns the position of the joint in quaternions when given the name of the joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The position of the joint in quaternions
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["quaternion"]

    def getJointLocalRotationByName(self, joint_name: str):
        """
        Returns the local rotational orientation of the joint when given the name of the joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The local rotational orientation of the joint
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["local_rotation"]

    def getJointLocalQuaternionByName(self, joint_name: str):
        """
        Returns the local position of the joint in quaternions when given the name of the joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The local position of the joint in quaternions
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["local_quaternion"]

    def getJointVelocityByName(self, joint_name: str):
        """
        Returns the current velocity of a given joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The current velocity of the joint
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["velocity"]

    def getJointRotationByName(self, joint_name: str):
        """
        Returns the current rotational orientation of a given joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The current rotational orientation of the joint
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["joint_position"]

    def getJointAccelerationByName(self, joint_name: str):
        """
        Returns the current acceleration of a given joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The current acceleration of the joint
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["acceleration"]

    def getJointForceByName(self, joint_name: str):
        """
        Returns the current force acting on a given joint

        Args:
            joint_name: the name of the joint (or bone)

        Returns: The current force on the joint
        """
        joint_states = self.getJointStateByName(joint_name)
        return joint_states["joint_force"]

    def saveArticulationBoneData(self, path: str):
        """
        Saves the articulation bone data of an instance by sending a "SaveArticulationBoneData" action to the instance channel with the specified file path.

        Args:
            path: The file path where the articulation bone data will be saved.

        Returns: does not return anything
        """
        self.env.instance_channel.set_action(
            "SaveArticulationBoneData", id=self.id, path=path
        )