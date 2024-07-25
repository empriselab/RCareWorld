import pyrcareworld.attributes as attr


class GameObjectAttr(attr.BaseAttr):
    """
    Basic game object attribute class.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by internal function.

        Returns:
            Dict: A dict containing useful information of this class.

            self.data['3d_bounding_box']: The 3d bounding box of objects.
        """
        super().parse_message(data)

    def SetColor(self, color: list):
        """
        Set object color.

        Args:
            color: A list of length 4, represenging r, g, b and a. Each float is in range (0, 1).
        """
        if color is not None:
            assert len(color) == 4, "color length must be 4"
            color = [float(i) for i in color]

        self._send_data("SetColor", color)

    def EnabledRender(self, enabled: bool):
        """
        Enable or disable rendering system.

        Args:
            enabled: Bool, Ture for enable rendering and False for disable rendering.
        """
        self._send_data("EnabledRender", enabled)

    def SetTexture(self, path: str):
        """
        Set the texture of object.

        Args:
            path: Str, the absolute path for texture file.
        """
        self._send_data("SetTexture", path)

    def Get3DBBox(self):
        """
        Get the 3d bounding box of this object.

        """
        self._send_data("Get3DBBox")
