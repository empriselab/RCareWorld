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
        self.env._step()  # Ensure a step is made to process the command
        print("GetParticles command sent")
        
                # Wait for the data to be returned and processed
        while 'particles' not in self.data:
            self.env._step()
        
        # Return the particles data
        return self.data['particles']


    def AddAttach(self, id: int, max_dis: float = 0.03):
        """
        Add Attach clothing to attr object with the given ID.

        :param id: Int, Target attr object ID.
        :param max_dis: Float, max distance.
        """
        self._send_data("AddAttach", int(id), float(max_dis))

    def RemoveAttach(self, id: int):
        """
        Remove Attach clothing from attr object with the given ID.

        :param id: Int, Target attr object ID.
        """
        self._send_data("RemoveAttach", int(id))
