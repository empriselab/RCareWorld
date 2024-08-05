import pyrcareworld.attributes as attr

class SpongeAttr(attr.BaseAttr):
    """
    Sponge attribute class to interact with the sponge in the Unity environment.
    """
        

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
