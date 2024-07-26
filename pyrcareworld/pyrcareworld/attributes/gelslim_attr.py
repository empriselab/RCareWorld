import base64
import pyrcareworld.attributes as attr


class GelSlimAttr(attr.BaseAttr):
    """
    Class for simulating GelSlim tactile sensor.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by internal function.

        Returns:
            Dict: A dict containing useful information of this class.

            self.data['light']: Bytes of RGB light image in GelSlim.

            self.data['depth']: Bytes of depth image in GelSlim.
        """
        super().parse_message(data)
        if "light" in self.data:
            self.data["light"] = base64.b64decode(self.data["light"])
        if "depth" in self.data:
            self.data["depth"] = base64.b64decode(self.data["depth"])

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