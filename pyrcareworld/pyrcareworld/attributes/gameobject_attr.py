import pyrcareworld.attributes as attr

class GameObjectAttr(attr.BaseAttr):
    """
    Basic game object attribute class.
    
    The data stored in self.data is a dictionary containing the following keys:
     - '3d_bounding_box': The 3D bounding box of objects.
    """


    def SetColor(self, color: list):
        """
        Set the object color.

        :param color: A list of length 4, representing r, g, b, and a. Each float is in the range (0, 1).
        """
        if color is not None:
            assert len(color) == 4, "color length must be 4"
            color = [float(i) for i in color]

        self._send_data("SetColor", color)

    def EnabledRender(self, enabled: bool):
        """
        Enable or disable the rendering system.

        :param enabled: Bool, True to enable rendering and False to disable rendering.
        """
        self._send_data("EnabledRender", enabled)

    def SetTexture(self, path: str):
        """
        Set the texture of the object.

        :param path: Str, the absolute path for the texture file.
        """
        self._send_data("SetTexture", path)

    def Get3DBBox(self):
        """
        Get the 3D bounding box of this object.
        """
        self._send_data("Get3DBBox")
