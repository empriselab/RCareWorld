import pyrcareworld.attributes as attr


class ColliderAttr(attr.GameObjectAttr):
    """
    Collider class for objects who have collider in Unity.
    """

    def EnabledAllCollider(self, enabled: bool):
        """
        Set the collider enabled or unenabled.

        Args:
            active: Bool, True for enable and False for unenable.
        """
        self._send_data("EnabledAllCollider", enabled)

    def SetPhysicMaterial(
        self,
        bounciness: float,
        dynamicFriction: float,
        staticFriction: float,
        frictionCombine: int,
        bounceCombine: int,
    ):
        """
        Set the collider physical material.

        Args:
            bounciness (float): The coefficient of restitution or "bounciness" of the collider. It determines how much
                kinetic energy is retained after a collision. A value of 0 means no bounce, while a value of 1 means a
                perfect bounce.
            dynamicFriction (float): The coefficient of friction when the collider is in motion relative to another
                collider. It determines how much resistance there is when the collider is sliding against another surface.
            staticFriction (float): The coefficient of friction when the collider is at rest relative to another collider.
                It determines the resistance to initiating motion between the collider and another surface.
            frictionCombine (int): An integer representing how friction values should be combined when multiple colliders
                interact. It can take on values such as:
                - 0: Average
                - 1: Maximum
                - 2: Minimum
                - 3: Multiply
                These values define how friction will be calculated when multiple colliders are in contact.
            bounceCombine (int): An integer representing how bounce values should be combined when multiple colliders
                interact. It can take on values such as:
                - 0: Average
                - 1: Maximum
                - 2: Minimum
                - 3: Multiply
                These values define how bounciness will be calculated when multiple colliders are in contact.
        """
        self._send_data(
            "SetPhysicMaterial",
            float(bounciness),
            float(dynamicFriction),
            float(staticFriction),
            int(frictionCombine),
            int(bounceCombine),
        )

    def SetRFMoveColliderActive(self, active: bool):
        """
        Set the collider active or inactive in RFMove.

        Args:
            active: Bool, True for active and False for inactive.
        """
        self._send_data("SetRFMoveColliderActive", active)

    def GenerateVHACDColider(self):
        """
        Generate convex colliders using VHACD algorithm.
        """
        self._send_data("GenerateVHACDColider")

    def AddObiCollider(self):
        """
        Add ObiCollider for this Collider.
        """
        self._send_data("AddObiCollider")
