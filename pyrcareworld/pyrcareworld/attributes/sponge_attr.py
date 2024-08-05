import pyrcareworld.attributes as attr

class SpongeAttr(attr.BaseAttr):
    """
    Sponge attribute class to interact with the sponge in the Unity environment.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

        data['paint_proportion']: Proportion of paint.
        data['forces']: A list of force values.
        """
        super().parse_message(data)
        self.data.update(data)

    def GetPaintProportion(self):
        """
        Get the proportion of the paint on the avatar.
        """
        return self.data.get("paint_proportion", 0.0)

    def GetEffectiveForceProportion(self):
        """
        Get the proportion of effective forces (force within 2 to 12 range).
        """
        return self.data.get("effective_force_proportion", 0.0)

    def GetForce(self):
        """
        Get the force on the sponge.
        """
        return self.data.get("real_time_forces", [0.0]) 