import pyrcareworld.attributes as attr

class SpongeAttr(attr.BaseAttr):
    """
    Sponge attribute class to interact with the sponge in the Unity environment.
    """

    def __init__(self, attr_id: int):
        """
        Initialize the SpongeAttr class.

        :param attr_id: The unique identifier of the sponge attribute.
        :type attr_id: int
        """
        super().__init__(attr_id)
        self.paint_proportion = 0
        self.effective_force_proportion = 0
        self.real_time_forces = []
        self.paint_proportion = 0
        
    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by internal function.
        """
        super().parse_messaget("paint_proportion")
        super().parse_message("effective_force_proportion")
        super().parse_message("real_time_forces")
        
        return {
            "paint_proportion": self.paint_proportion,
            "effective_force_proportion": self.effective_force_proportion,
            "real_time_forces": self.real_time_forces,
        }

    def GetPaintProportion(self):
        """
        Get the proportion of the paint on the avatar.
        """
        self.paint_proportion = super().parse_message("paint_proportion")
        
        return{
            "paint_proportion": self.paint_proportion
        }

    def GetEffectiveForceProportion(self):
        """
        Get the proportion of effective forces (force within 2 to 12 range).
        """
        self.effective_force_proportion = super().parse_message("effective_force_proportion")
        
        return {
            "effective_force_proportion": self.effective_force_proportion
        }

    def GetRealTimeForces(self):
        """
        Get the real-time forces recorded by the sponge.
        """
        self._send_data = super().parse_message("real_time_forces")
        
        return {
            "real_time_forces": self.real_time_forces
        }
