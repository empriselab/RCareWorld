import base64
import pyrcareworld.attributes as attr


class GelSlimAttr(attr.BaseAttr):
    """
    Class for simulating GelSlim tactile sensor.

    In addition to the default keys in messages received from Unity
    expected by BaseAttr, the following are expected in this class:

        'light': Bytes of RGB light image in DIGIT.

        'depth': Bytes of depth image in DIGIT.
    """

    def GetData(self):
        """
        Get data from GelSlim.
        """
        self._send_data("GetData")

    def BlurGel(self, radius: int = 5, sigma: float = 2):
        """
        Blur Gel mesh. Simulate smooth deformation.

        Args:
            radius: Int, Gaussian blur radius.
            sigma: Float, Gaussian blur sigma.
        """
        self._send_data("BlurGel", int(radius), float(sigma))

    def RestoreGel(self):
        """
        Restore Gel mesh.
        """
        self._send_data("RestoreGel")