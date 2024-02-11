from abc import ABC
from pyrcareworld.utils import pose_convert


class RCareWorldBaseObject(ABC):
    """
    Base Object
    """

    def __init__(self, env, id: int, name: str, is_in_scene: bool = False):
        """
        Initialization function.
        @param env: The environment object
        @param id: ID of this robot
        """
        self.env = env
        self.id = id
        self.is_in_scene = is_in_scene
        self.object_type = "base_object"
        self.name = name
        self.copy_ids = []

    def load(self, position=None, rotation=[0,0,0]) -> None:
        """
        Load object into the Scene in Unity
        The object need to be an addressbale file and not in scene.
        """
        assert (
            self.is_in_scene is False
        ), "The object is already in the scene, no need to load again."

        self.env.asset_channel.set_action("InstanceObject", id=self.id, name=self.name)
        if position is not None:
            self.env.instance_channel.set_action(
                "SetTransform", id=self.id, position=position, rotation=rotation
            )
        else:
            self.env.instance_channel.set_action(
                "SetTransform", id=self.id, position=[0, 0, 0], rotation=rotation
            )

        self.is_in_scene = True

    def destroy(self):
        """
        Destroy the object in the scene.
        """
        self.env.instance_channel.set_action("Destroy", id=self.id)
        self.is_in_scene = False

    def copy(self, copy_id: int):
        """
        Make a copy of the object in the scene. The copy is assigned with `copy_id`.
        """
        self.copy_ids.append(copy_id)
        self.env.instance_channel.set_action("Copy", id=self.id, copy_id=copy_id)
        self.env._step()
        new_object = RCareWorldBaseObject(
            self.env, copy_id, self.name + "_copy", is_in_scene=True
        )
        return new_object

    def setTransform(
        self,
        position: list = None,
        rotation: list = None,
        scale: list = None,
        is_world: bool = True,
    ):
        """Set the transform of a object, specified by id.
        Args:
        Compulsory:
        id: The id of object.

        Optional:
        position: A 3-d list inferring object's position, in [x,y,z] order.
        rotation: A 3-d list inferring object's rotation, in [x,y,z] order.
        scale: A 3-d list inferring object's rotation, in [x,y,z] order.
        is_world: bool, indicating if the transform is in world frame, by default true
        """
        if None not in (position, rotation, scale):
            self.env.instance_channel.set_action(
                "SetTransform",
                id=self.id,
                position=position,
                rotation=rotation,
                scale=scale,
                is_world=is_world,
            )
        elif None not in (position, rotation) and scale is None:
            self.env.instance_channel.set_action(
                "SetTransform",
                id=self.id,
                position=position,
                rotation=rotation,
                is_world=is_world,
            )
        elif None not in (position, scale) and rotation is None:
            self.env.instance_channel.set_action(
                "SetTransform",
                id=self.id,
                position=position,
                scale=scale,
                is_world=is_world,
            )
        elif None not in (rotation, scale) and position is None:
            self.env.instance_channel.set_action(
                "SetTransform",
                id=self.id,
                rotation=rotation,
                scale=scale,
                is_world=is_world,
            )
        elif position is None and rotation is None and scale is not None:
            self.env.instance_channel.set_action(
                "SetTransform", id=self.id, scale=scale, is_world=is_world
            )
        elif rotation is None and scale is None and position is not None:
            self.env.instance_channel.set_action(
                "SetTransform", id=self.id, position=position, is_world=is_world
            )
        elif scale is None and position is None and rotation is not None:
            self.env.instance_channel.set_action(
                "SetTransform", id=self.id, rotation=rotation, is_world=is_world
            )

    def getThisObjectState(self):
        """
        Get the state of this object. The state is a dictionary. It contains the following keys:
        position: The xyz position of this object. It is in world frame, in right hand system.
        rotation: The rotation of this object. It is in euler angle (xyz) format in right hand system.
        local_position: The local position of this object. It is in local frame, in right hand system.
        local_rotation: The local rotation of this object. It is in euler angle (xyz) format in right hand system.
        """
        return self.env.instance_channel.data[int(self.id)]

    def getPosition(self):
        """
        Get the  xyz position of this object. It is in world frame, in right hand system.
        """

        info = self.env.instance_channel.data[self.id]
        position = info["position"]
        return position

    def getLocalPosition(self):
        """
        Get the local position of this object. It is in local frame, in right hand system.
        """
        info = self.env.instance_channel.data[self.id]
        local_position = info["local_position"]
        return local_position

    def getRotation(self):
        """
        Get the rotation of this object. It is in euler angle (xyz) format in right hand system.
        """
        info = self.env.instance_channel.data[self.id]
        rotation = info["rotation"]
        return rotation

    def getLocalRotation(self):
        """
        Get the local rotation of this object. It is in euler angle (xyz) format in right hand system.
        """
        info = self.env.instance_channel.data[self.id]
        local_rotation = info["local_rotation"]
        return local_rotation

    def getQuaternion(self):
        """
        Get the quaternion of this object. It is in [x,y,z,w] format in right hand system.
        """
        info = self.env.instance_channel.data[self.id]
        quaternion = info["quaternion"]
        return quaternion

    def getLocalQuaternion(self):
        """
        Get the local quaternion of this object. It is in [x,y,z,w] format in right hand system.
        """
        info = self.env.instance_channel.data[self.id]
        local_quaternion = info["local_quaternion"]
        return local_quaternion

    def getLocalPositionFromWorld(self, position: list) -> list:
        """
        Get the local position of this object. It is in local frame, in right hand system.
        """
        local_pose = self.env.instance_channel.set_action(
            "GetLoaclPointFromWorld", id=self.id, point=position
        )
        return local_pose

    def getWorldPositionFromLocal(self, position: list) -> list:
        """
        Get the local position of this object. It is in local frame, in right hand system.
        """
        world_pose = self.env.instance_channel.set_action(
            "getWorldPositionFromLocal", id=self.id, point=position
        )
        return world_pose

    def setActive(self, active: bool):
        """
        Activate or deactivate this object.
        """
        self.env.instance_channel.set_action("SetActive", id=self.id, active=active)

    def setParent(self, parent):
        """
        Set the parent of this object.
        """
        parent_id = parent.id
        parent_name = parent.name
        parent_id = int(parent_id)
        parent_name = str(parent_name)
        self.env.instance_channel.set_action(
            "SetParent", id=self.id, parent_id=parent_id, parent_name=parent_name
        )

    def setParentByID(self, parent_id):
        """
        Set the parent of this object.
        """
        self.env.instance_channel.set_action(
            "SetParent", id=self.id, parent_id=parent_id, parent_name="Parent"
        )

    def unsetParent(self):
        """
        Unset the parent of this object.
        """
        self.env.instance_channel.set_action(
            "SetParent", id=self.id, parent_id=-1, parent_name=""
        )

    def setLayer(self, layer: int):
        self.env.instance_channel.set_action("SetLayer", id=self.id, layer=layer)

    def setRotationQuaternion(self, quaternion, is_world: bool = True) -> None:
        self.env.instance_channel.set_action(
            "SetRotationQuaternion",
            id=self.id,
            quaternion=quaternion,
            is_world=is_world,
        )
