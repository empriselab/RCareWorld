import pyrcareworld.attributes as attr

class ColliderAttr(attr.GameObjectAttr):
    """
    Collider class for objects that have a collider in Unity.
    """

    def EnabledAllCollider(self, enabled: bool):
        """
        Enable or disable all colliders.

        :param enabled: Bool, True to enable and False to disable.
        """
        self._send_data("EnabledAllCollider", enabled)

    def SetPhysicMaterial(self, bounciness: float, dynamicFriction: float, staticFriction: float, frictionCombine: int, bounceCombine: int):
        """
        Set the physical material properties for the collider.

        :param bounciness: Float, The coefficient of restitution or "bounciness" of the collider. A value of 0 means no bounce, while a value of 1 means a perfect bounce.
        :param dynamicFriction: Float, The coefficient of friction when the collider is in motion relative to another collider.
        :param staticFriction: Float, The coefficient of friction when the collider is at rest relative to another collider.
        :param frictionCombine: Int, Defines how friction values should be combined when multiple colliders interact. Possible values:
            - 0: Average
            - 1: Maximum
            - 2: Minimum
            - 3: Multiply
        :param bounceCombine: Int, Defines how bounce values should be combined when multiple colliders interact. Possible values:
            - 0: Average
            - 1: Maximum
            - 2: Minimum
            - 3: Multiply
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

        :param active: Bool, True for active and False for inactive.
        """
        self._send_data("SetRFMoveColliderActive", active)

    def GenerateVHACDColider(self):
        """
        Generate convex colliders using the VHACD algorithm.
        """
        self._send_data("GenerateVHACDColider")

    def AddObiCollider(self):
        """
        Add an ObiCollider to this Collider. https://obi.virtualmethodstudio.com/manual/6.3/collisions.html
        """
        self._send_data("AddObiCollider")
