class BaseAttr:
    """
    Base attribute class, which includes general functions such as
    object loading, deleting and transforming.
    """

    def __init__(self, env, id: int, data: dict = {}):
        self.env = env
        self.id = id
        self.data = data

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by internal function.

        Returns:
            Dict: A dict containing useful information of this class.

            self.data['name']: The name of the object.

            self.data['position']: The position of the object in world coordinates.

            self.data['rotation']: The euler angle of the object in world coordinates.

            self.data['quaternion']: The quaternion of the object in world coordinates.

            self.data['local_position']: The position of the object in its parent's local coordinates.

            self.data['local_rotation']: The euler angle of the object in its parent's local coordinates.

            self.data['local_quaternion']: The quaternion of the object in its parent's local coordinates.

            self.data['local_to_world_matrix']: The transformation matrix from local to world coordinates.

            self.data['result_local_point']: The result of transforming the object from local to world coordinates.

            self.data['result_world_point']: The result of transforming the object from world to local coordinates.
        """
        self.data = data

    def _send_data(self, message: str, *args):
        self.env._send_instance_data(self.id, message, *args)

    def SetType(self, attr_type: type):
        """
        Set the attribute type of this object

        Args:
            attr_type: Any attribute in pyrcareworld.attributes.

        Returns:
            The target attribute.
        """
        self.env.attrs[self.id] = attr_type(self.env, self.id, self.data)
        return self.env.attrs[self.id]

    def SetTransform(
        self,
        position: list = None,
        rotation: list = None,
        scale: list = None,
        is_world: bool = True,
    ):
        """
        Set the transform of this object, including position, rotation, scale and coordinate.

        Args:
            position: A list of length 3, representing the target position value of object.
            rotation: A list of length 3, representing the target euler angle value of object.
            scale: A list of length 3, representing the target scale value of object.
            is_world: Bool, True for world coordinate, False for local coordinate.
        """
        if position is not None:
            assert len(position) == 3, "position length must be 3"
            position = [float(i) for i in position]
        if rotation is not None:
            assert len(rotation) == 3, "rotation length must be 3"
            rotation = [float(i) for i in rotation]
        if scale is not None:
            assert len(scale) == 3, "scale length must be 3"
            scale = [float(i) for i in scale]

        self._send_data("SetTransform", position, rotation, scale, is_world)

    def SetPosition(self, position: list = None, is_world: bool = True):
        """
        Set the position of this object

        Args:
            position: A list of length 3, representing the target position value of object.
            is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(position) == 3, "position length must be 3"
        position = [float(i) for i in position]

        self._send_data("SetPosition", position, is_world)

    def SetRotation(self, rotation: list = None, is_world: bool = True):
        """
        Set the rotation of this object

        Args:
            rotation: A list of length 3, representing the target euler angle value of object.
            is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(rotation) == 3, "rotation length must be 3"
        rotation = [float(i) for i in rotation]

        self._send_data("SetRotation", rotation, is_world)

    def SetRotationQuaternion(self, quaternion: list = None, is_world: bool = True):
        """
        Rotate this object using quaternion.

        Args:
            quaternion: A list of length 4, representing the quaternion from current pose.
            is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(quaternion) == 4, "quaternion length must be 4"
        quaternion = [float(i) for i in quaternion]

        self._send_data("SetRotationQuaternion", quaternion, is_world)

    def SetScale(self, scale: list = None):
        """
        Set the scale of this object

        Args:
            scale: A list of length 3, representing the target scale value of object.
        """
        assert len(scale) == 3, "scale length must be 3"
        scale = [float(i) for i in scale]

        self._send_data("SetScale", scale)

    def Translate(self, translation: list, is_world: bool = True):
        """
        Translate this object.

        Args:
            translation: A list of length 3, representing the translation from current position.
            is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(translation) == 3, "translation length must be 3"
        translation = [float(i) for i in translation]

        self._send_data("Translate", translation, is_world)

    def Rotate(self, rotation: list, is_world: bool = True):
        """
        Rotate this object.

        Args:
            rotation: A list of length 3, representing the euler-angle-format rotation from current euler angle.
            is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(rotation) == 3, "rotation length must be 3"
        rotation = [float(i) for i in rotation]

        self._send_data("Rotate", rotation, is_world)

    def LookAt(self, target: list, world_up: list = None):
        """
        Rotates the transform so the forward vector points at target's current position.

        Args:
            target: A list of length 3, target to point towards.
            world_up: A list of length 3, vector specifying the upward direction.
        """
        if world_up is None:
            world_up = [0.0, 1.0, 0.0]
        assert len(target) == 3, "target length must be 3"
        target = [float(i) for i in target]
        assert len(world_up) == 3, "world_up length must be 3"
        world_up = [float(i) for i in world_up]

        self._send_data("LookAt", target, world_up)

    def SetActive(self, active: bool):
        """
        Set the activeness of this object.

        Args:
            active: Bool, True for active, False for inactive.
        """
        self._send_data("SetActive", active)

    def SetParent(self, parent_id: int, parent_name: str = ""):
        """
        Set the parent of this object.

        Args:
            parent_id: Int, the id of parent object.
            parent_name: Str, the name of parent object.
        """
        self._send_data("SetParent", parent_id, parent_name)

    def SetLayer(self, layer: int):
        """
        Set the layer in Unity of this object.

        Args:
            layer: Int, the number of layer.
        """
        self._send_data("SetLayer", layer)

    def Copy(self, new_id: int):
        """
        Duplicate an object.

        Args:
            new_id: Int, the id of new object.
        """
        self._send_data("Copy", new_id)

        self.env.attrs[new_id] = type(self)(self.env, new_id, self.data)
        return self.env.attrs[new_id]

    def Destroy(self):
        """
        Destroy this object in Unity.
        """
        self._send_data("Destroy")

        self.env.attrs.pop(self.id)

    def GetLocalPointFromWorld(self, point: list):
        """
        Transform a point from local coordinates to world coordinates. After calling this method and stepping once, the result will be saved in self.data['result_local_point']

        Args:
            point: A list of length 3, representing the position of a point.
        """
        assert len(point) == 3, "point length must be 3"
        point = [float(i) for i in point]

        self._send_data("GetLocalPointFromWorld", point)

    def GetWorldPointFromLocal(self, point: list):
        """
        Transform a point from world coordinates to local coordinates. After calling this method and stepping once, the result will be saved in self.data['result_world_point']

        Args:
            point: A list of length 3, representing the position of a point.
        """
        assert len(point) == 3, "point length must be 3"
        point = [float(i) for i in point]

        self._send_data("GetWorldPointFromLocal", point)

    def DoMove(
        self,
        position: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Tween movement.

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
            "DoMove", position, float(duration), speed_based, relative
        )

    def DoRotate(
        self,
        rotation: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Tween rotation.

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
            "DoRotate", rotation, float(duration), speed_based, relative
        )

    def DoRotateQuaternion(
        self,
        quaternion: list,
        duration: float,
        speed_based: bool = True,
        relative: bool = False,
    ):
        """
        Tween rotation using quaternion.

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
            "DoRotateQuaternion",
            quaternion,
            float(duration),
            speed_based,
            relative,
        )

    def DoComplete(self):
        """
        Tween movement / rotation complete directly.
        """
        self._send_data("DoComplete")

    def DoKill(self):
        """
        Tween movement / rotation stop.
        """
        self._send_data("DoKill")

    def WaitDo(self):
        """
        Wait for the native IK target movement / rotation complete.
        """
        self.env._step()
        while not self.data["move_done"] or not self.data["rotate_done"]:
            self.env._step()
