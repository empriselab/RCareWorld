import pyrcareworld.attributes as attr

class RigidbodyAttr(attr.ColliderAttr):
    """
    Rigid body class.
    
    The data stored in self.data is a dictionary containing the following keys:
    - 'velocity': The velocity of the object.
    - 'angular_velocity': The angular velocity of the object.
    """

    def SetMass(self, mass: float):
        """
        Set the mass of this rigid body object.

        :param mass: Float, representing the mass of this rigid body.
        """
        self._send_data("SetMass", float(mass))

    def SetDrag(self, drag: float):
        """
        Set the drag of this rigid body object.

        :param drag: Float, representing the drag of this rigid body.
        """
        self._send_data("SetDrag", float(drag))

    def SetAngularDrag(self, angular_drag: float):
        """
        Set the angular drag of this rigid body object.

        :param angular_drag: Float, representing the angular drag of this rigid body.
        """
        self._send_data("SetAngularDrag", float(angular_drag))

    def SetUseGravity(self, use_gravity: bool):
        """
        Set the rigid body to use gravity or not.

        :param use_gravity: Bool, use gravity or not.
        """
        self._send_data("SetUseGravity", use_gravity)

    def EnabledMouseDrag(self, enabled: bool):
        """
        Enable or disable the rigid body Mouse Drag.

        :param enabled: Bool, enable Mouse Drag or not.
        """
        self._send_data("EnabledMouseDrag", enabled)

    def AddForce(self, force: list):
        """
        Add force to this rigid body object.

        :param force: A list of length 3, representing the force added to this rigid body.
        """
        if force is not None:
            force = [float(i) for i in force]

        self._send_data("AddForce", force)

    def SetVelocity(self, velocity: list):
        """
        Set the velocity of this rigid body object.

        :param velocity: A list of length 3, representing the velocity of this rigid body.
        """
        if velocity is not None:
            velocity = [float(i) for i in velocity]

        self._send_data("SetVelocity", velocity)

    def SetAngularVelocity(self, angular_velocity: list):
        """
        Set the angular velocity of this rigid body object.

        :param angular_velocity: A list of length 3, representing the angular velocity of this rigid body.
        """
        if angular_velocity is not None:
            angular_velocity = [float(i) for i in angular_velocity]

        self._send_data("SetAngularVelocity", angular_velocity)

    def SetKinematic(self, is_kinematic: bool):
        """
        Set the Rigidbody to be kinematic or not.

        :param is_kinematic: Bool, True if the Rigidbody is kinematic, False otherwise.
        """
        self._send_data("SetKinematic", is_kinematic)

    def Link(self, target_id: int, joint_index: int = 0, mass_scale: float = 1, connected_mass_scale: float = 1):
        """
        Link this rigidbody to another rigidbody or ArticulationBody.

        :param target_id: Int, the ID of another rigidbody or ControllerAttr.
        :param joint_index: Int, the ID of the ControllerAttr joint.
        :param mass_scale: Float, the scale to apply to the inverse mass and inertia tensor of the body prior to solving the constraints.
        :param connected_mass_scale: Float, the scale to apply to the inverse mass and inertia tensor of the connected body prior to solving the constraints.
        """
        self._send_data("Link", int(target_id), int(joint_index), float(mass_scale), float(connected_mass_scale))
