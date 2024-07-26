import pyrcareworld.attributes as attr


class RigidbodyAttr(attr.ColliderAttr):
    """
    Rigid body class.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by internal function.

        Returns:
            Dict: A dict containing useful information of this class.

            self.data['velocity']: The velocity of the object.

            self.data['angular_velocity']: The angular velcity of the object.
        """
        super().parse_message(data)

    def SetMass(self, mass: float):
        """
        Set the mass of this rigid body object

        Args:
            mass: Float, representing the mass of this rigid body.
        """
        self._send_data("SetMass", float(mass))

    def SetDrag(self, drag: float):
        """
        Set the drag of this rigid body object

        Args:
            drag: Float, representing the drag of this rigid body.
        """
        self._send_data("SetDrag", float(drag))

    def SetAngularDrag(self, angular_drag: float):
        """
        Set the angular drag of this rigid body object

        Args:
            angular_drag: Float, representing the angular drag of this rigid body.
        """
        self._send_data("SetAngularDrag", float(angular_drag))
    def SetUseGravity(self, use_gravity: bool):
        """
        Set the rigid body use gravity or not.

        Args:
            use_gravity: Bool, use gravity or not.
        """
        self._send_data("SetUseGravity", use_gravity)

    def EnabledMouseDrag(self, enabled: bool):
        """
        Enable or Disable the rigid body Mouse Drag.

        Args:
            enabled: Bool, Enabled Mouse Drag or not.
        """
        self._send_data("EnabledMouseDrag", enabled)

    def AddForce(self, force: list):
        """
        Add force to this rigid body object.

        Args:
            force: A list of length 3, representing the force added to this rigid body.
        """
        if force is not None:
            force = [float(i) for i in force]

        self._send_data("AddForce", force)

    def SetVelocity(self, velocity: list):
        """
        Set the velocity of this rigid body object.

        Args:
            velocity: A list of length 3, representing the velocity of this rigid body.
        """
        if velocity is not None:
            velocity = [float(i) for i in velocity]

        self._send_data("SetVelocity", velocity)

    def SetAngularVelocity(self, angular_velocity: list):
        """
        Set the angular velocity of this rigid body object.

        Args:
            angular_velocity: A list of length 3, representing the angular velocity of this rigid body.
        """
        if angular_velocity is not None:
            angular_velocity = [float(i) for i in angular_velocity]

        self._send_data("SetAngularVelocity", angular_velocity)

    def SetKinematic(self, is_kinematic: bool):
        """
        Set the Rigidbody is kinematic or not.

        Args:
            is_kinematic: is kinematic or not.
        """
        self._send_data("SetKinematic", is_kinematic)

    def Link(self, target_id: int, joint_index: int = 0, mass_scale: float = 1, connected_mass_scale: float = 1):
        """
        Link this rigidbody to another rigidbody or ArticulationBody

        Args:
            target_id: id of another rigidbody or ControllerAttr.
            joint_index: id of ControllerAttr joint.
            mass_scale: The scale to apply to the inverse mass and inertia tensor of the body prior to solving the constraints.
            connected_mass_scale: The scale to apply to the inverse mass and inertia tensor of the connected body prior to solving the constraints.
        """
        self._send_data("Link", int(target_id), int(joint_index), float(mass_scale), float(connected_mass_scale))
