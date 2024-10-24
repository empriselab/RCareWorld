
import pyrcareworld.attributes as attr


class PersonRandomizerAttr(attr.BaseAttr):
    """
    Person Randomizer attribute class.
    """
    def SetSeed(self, seed: int):
        """
        Set the random seed.

        Args:
            seed: Int, random seed.
        """
        self._send_data("SetSeed", seed)
