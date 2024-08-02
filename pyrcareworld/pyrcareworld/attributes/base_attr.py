class BaseAttr:
    """
    Base attribute class, which includes general functions such as
    object loading, setting transform, setting parent, etc.
    """

    def __init__(self, env, id: int, data: dict = {}):
        """
        Initialize the BaseAttr.

        :param env: Environment object.
        :param id: ID of the object.
        :param data: Optional initial data.
        """
        self.env = env
        self.id = id
        self.data = data

    def parse_message(self, data: dict):
        """
        Parse messages. 
        This function handles the data sent from Unity and stores it in self.data, which contains the keys in `data`.
        This function is called by an internal function at each timestep, so the data is updated every timestep.

        :param data: Dictionary containing the message data. The keys are:
            - 'name': The name of the object.
            - 'position': The position of the object in world coordinates.
            - 'rotation': The euler angle of the object in world coordinates.
            - 'quaternion': The quaternion of the object in world coordinates.
            - 'local_position': The position of the object in its parent's local coordinates.
            - 'local_rotation': The euler angle of the object in its parent's local coordinates.
            - 'local_quaternion': The quaternion of the object in its parent's local coordinates.
            - 'local_to_world_matrix': The transformation matrix from local to world coordinates.
            - 'result_local_point': The result of transforming the object from local to world coordinates.
            - 'result_world_point': The result of transforming the object from world to local coordinates.
        """
        self.data = data

    def _send_data(self, message: str, *args):
        """
        Send data to the environment.

        :param message: The message to send.
        :param args: Additional arguments for the message.
        """
        self.env._send_instance_data(self.id, message, *args)

    def SetType(self, attr_type: type):
        """
        Set the attribute type of this object.

        :param attr_type: Any attribute in pyrcareworld.attributes.
        :return: The target attribute.
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
        Set the transform of this object, including position, rotation, scale, and coordinate.

        :param position: A list of length 3, representing the target position value of the object.
        :param rotation: A list of length 3, representing the target euler angle value of the object.
        :param scale: A list of length 3, representing the target scale value of the object.
        :param is_world: Bool, True for world coordinate, False for local coordinate.
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
        Set the position of this object.

        :param position: A list of length 3, representing the target position value of the object.
        :param is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(position) == 3, "position length must be 3"
        position = [float(i) for i in position]

        self._send_data("SetPosition", position, is_world)

    def SetRotation(self, rotation: list = None, is_world: bool = True):
        """
        Set the rotation of this object.

        :param rotation: A list of length 3, representing the target euler angle value of the object.
        :param is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(rotation) == 3, "rotation length must be 3"
        rotation = [float(i) for i in rotation]

        self._send_data("SetRotation", rotation, is_world)

    def SetRotationQuaternion(self, quaternion: list = None, is_world: bool = True):
        """
        Set the rotation of this object using quaternion.

        :param quaternion: A list of length 4, representing the quaternion from the current pose.
        :param is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(quaternion) == 4, "quaternion length must be 4"
        quaternion = [float(i) for i in quaternion]

        self._send_data("SetRotationQuaternion", quaternion, is_world)

    def SetScale(self, scale: list = None):
        """
        Set the scale of this object.

        :param scale: A list of length 3, representing the target scale value of the object.
        """
        assert len(scale) == 3, "scale length must be 3"
        scale = [float(i) for i in scale]

        self._send_data("SetScale", scale)

    def Translate(self, translation: list, is_world: bool = True):
        """
        Translate this object.

        :param translation: A list of length 3, representing the translation from the current position.
        :param is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(translation) == 3, "translation length must be 3"
        translation = [float(i) for i in translation]

        self._send_data("Translate", translation, is_world)

    def Rotate(self, rotation: list, is_world: bool = True):
        """
        Rotate this object.

        :param rotation: A list of length 3, representing the euler-angle-format rotation from the current euler angle.
        :param is_world: Bool, True for world coordinate, False for local coordinate.
        """
        assert len(rotation) == 3, "rotation length must be 3"
        rotation = [float(i) for i in rotation]

        self._send_data("Rotate", rotation, is_world)

    def LookAt(self, target: list, world_up: list = None):
        """
        Rotate the transform so the forward vector points at the target's current position.

        :param target: A list of length 3, target to point towards.
        :param world_up: A list of length 3, vector specifying the upward direction.
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
        Activate/Deactivate this object.

        :param active: Bool, True for active, False for inactive.
        """
        self._send_data("SetActive", active)

    def SetParent(self, parent_id: int, parent_name: str = ""):
        """
        Set the parent of this object.

        :param parent_id: Int, the ID of the parent object.
        :param parent_name: Str, the name of the parent object.
        """
        self._send_data("SetParent", parent_id, parent_name)

    def SetLayer(self, layer: int):
        """
        Set the layer in Unity of this object. Check https://docs.unity3d.com/Manual/Layers.html to get an idea about layers.

        :param layer: Int, the number of the layer.
        """
        self._send_data("SetLayer", layer)

    def Copy(self, new_id: int):
        """
        Duplicate an object.

        :param new_id: Int, the ID of the new object.
        :return: The new duplicated object.
        """
        self._send_data("Copy", new_id)

        self.env.attrs[new_id] = type(self)(self.env, new_id, self.data)
        return self.env.attrs[new_id]

    def Destroy(self):
        """
        Destroy this object.
        """
        self._send_data("Destroy")

        self.env.attrs.pop(self.id)

    def GetLocalPointFromWorld(self, point: list):
        """
        Transform a point from local coordinates to world coordinates.
        After calling this method and stepping once, the result will be saved in self.data['result_local_point'].

        :param point: A list of length 3, representing the position of a point.
        """
        assert len(point) == 3, "point length must be 3"
        point = [float(i) for i in point]

        self._send_data("GetLocalPointFromWorld", point)

    def GetWorldPointFromLocal(self, point: list):
        """
        Transform a point from world coordinates to local coordinates.
        After calling this method and stepping once, the result will be saved in self.data['result_world_point'].

        :param point: A list of length 3, representing the position of a point.
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

        :param position: A list of length 3, representing the position.
        :param duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
        :param speed_based: Bool, determines if the movement is speed-based.
        :param relative: Bool, if True, `position` is relative; otherwise, `position` is absolute.
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

        :param rotation: A list of length 3, representing the rotation.
        :param duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
        :param speed_based: Bool, determines if the rotation is speed-based.
        :param relative: Bool, if True, `rotation` is relative; otherwise, `rotation` is absolute.
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

        :param quaternion: A list of length 4, representing the quaternion.
        :param duration: Float, if `speed_based` is True, it represents movement duration; otherwise, it represents movement speed.
        :param speed_based: Bool, determines if the rotation is speed-based.
        :param relative: Bool, if True, `quaternion` is relative; otherwise, `quaternion` is absolute.
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
        Complete tween movement/rotation directly.
        """
        self._send_data("DoComplete")

    def DoKill(self):
        """
        Stop tween movement/rotation.
        """
        self._send_data("DoKill")

    def WaitDo(self):
        """
        Wait for the native IK target movement/rotation to complete.
        """

        self.env._step()
        while not self.data["move_done"] or not self.data["rotate_done"]:
            self.env._step()
