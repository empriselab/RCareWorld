import base64
import pyrcareworld.attributes as attr

class DigitAttr(attr.BaseAttr):
    """
    Class for simulating DIGIT tactile sensor.
    https://digit.ml/
    The data stored in self.data is a dictionary containing the following keys:
        - 'light': Bytes of RGB light image in DIGIT.
        - 'depth': Bytes of depth image in DIGIT.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

        :param data: Dictionary containing the message data.
        """
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
