from enum import Enum
import pyrcareworld.attributes as attr

class LightType(Enum):
    """
    The type of light, keeping the same name as LightType (https://docs.unity3d.com/ScriptReference/LightType.html) in Unity.
    """
    Spot = 0
    Directional = 1
    Point = 2
    Area = 3  # unused
    Disc = 4  # unused

class LightShadow(Enum):
    """
    The type of shadow, keeping the same name as LightShadows (https://docs.unity3d.com/ScriptReference/LightShadows.html) in Unity.
    """
    NoneShadow = 0
    Hard = 1
    Soft = 2

class LightAttr(attr.BaseAttr):
    """
    Light attribute class.
    """


    def SetColor(self, color: list):
        """
        Set the color of the light.

        :param color: A list of length 3, representing the R, G, and B channels, in range [0, 1].
        """
        assert color is not None and len(color) == 3, "color length must be 3"
        color = [float(i) for i in color]

        self._send_data("SetColor", color)

    def SetType(self, light_type: LightType):
        """
        Set the type of light.

        :param light_type: LightType, the type of light.
        """
        self._send_data("SetType", light_type.value)

    def SetShadow(self, light_shadow: LightShadow):
        """
        Set the type of shadow.

        :param light_shadow: LightShadow, the type of shadow.
        """
        self._send_data("SetShadow", light_shadow.value)

    def SetIntensity(self, light_intensity: float):
        """
        Set the intensity of the light.

        :param light_intensity: Float, the intensity of the light.
        """
        self._send_data("SetIntensity", float(light_intensity))

    def SetRange(self, light_range: float):
        """
        Set the range of the light. (Only available when the LightType is `LightType.Spot` or `LightType.Point`)

        :param light_range: Float, the range of the light.
        """
        self._send_data("SetRange", float(light_range))

    def SetSpotAngle(self, spot_angle: float):
        """
        Set the angle of the light. (Only available when the LightType is `LightType.Spot`)

        :param spot_angle: Float, the angle of the light.
        """
        self._send_data("SetSpotAngle", float(spot_angle))
