import pyrcareworld.attributes as attr


class ClothAttr(attr.BaseAttr):
    """
    Obi cloth class.
    """

    def GetParticles(self):
        """
        Get the cloth particles.
        """
        self._send_data("GetParticles")

    def AddAttach(self, id: int, max_dis: float = 0.03):
        """
        Add Attach clothing to attr object with given ID

        Args:
            id: Int, Tatget attr object id.
            max_dis: Float, max distance.
        """
        self._send_data("AddAttach", int(id), float(max_dis))

    def RemoveAttach(self, id: int):
        """
        Remove Attach clothing to attr object with given ID

        Args:
            id: Int, Tatget attr object id.
        """
        self._send_data("RemoveAttach", int(id))
