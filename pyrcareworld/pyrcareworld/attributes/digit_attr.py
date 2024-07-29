import base64
import pyrcareworld.attributes as attr


class DigitAttr(attr.BaseAttr):
    """
    Class for simulating DIGIT tactile sensor.

    In addition to the default keys in messages received from Unity
    expected by BaseAttr, the following are expected in this class:

        'light': Bytes of RGB light image in DIGIT.

        'depth': Bytes of depth image in DIGIT.
    """

    def parse_message(self, data: dict):
        super().parse_message(data)
        if "light" in self.data:
            self.data["light"] = base64.b64decode(self.data["light"])
        if "depth" in self.data:
            self.data["depth"] = base64.b64decode(self.data["depth"])

    def GetData(self):
        """
        Get data from DIGIT.

        """
        self._send_data("GetData")