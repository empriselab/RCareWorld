from enum import Enum
import pyrcareworld.attributes as attr


class LightType(Enum):
    """
    The type of light, keeping same name with LightType (https://docs.unity3d.com/ScriptReference/LightType.html) in Unity.
    """

    Spot = 0
    Directional = 1
    Point = 2
    Area = 3  # unused
    Disc = 4  # unused


class LightShadow(Enum):
    """
    The type of shadow, keeping same name with LightShadows (https://docs.unity3d.com/ScriptReference/LightShadows.html) in Unity.
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
        Set the color of light.

        Args:
            color: A list of length 3, representing the R, G and B channel, in range [0, 1].
        """
        assert color is not None and len(color) == 3, "position length must be 3"
        color = [float(i) for i in color]

        self._send_data("SetColor", color)

    def SetType(self, light_type: LightType):
        """
        Set the type of light.

        Args:
            light_type: LightType, the type of light.
        """
        self._send_data("SetType", light_type.value)

    def SetShadow(self, light_shadow: LightShadow):
        """
        Set the type of shadow.

        Args:
            light_shadow: LightShadow, the type of the shadow.
        """
        self._send_data("SetShadow", light_shadow.value)

    def SetIntensity(self, light_intensity: float):
        """
        Set the intensity of light.

        Args:
            light_intensity: Float, the intensity of light.
        """
        self._send_data("SetIntensity", float(light_intensity))

    def SetRange(self, light_range: float):
        """
        Set the range of light. (Only available when the LightType is `LightType.Spot` or `LightType.Point`)

        Args:
            light_range: Float, the range of light.
        """
        self._send_data("SetRange", float(light_range))

    def SetSpotAngle(self, spot_angle: float):
        """
        Set the angle of light. (Only available when the LightType is `LightType.Spot`)

        Args:
            spot_angle: Float, the angle of light.
        """
        self._send_data("SetSpotAngle", float(spot_angle))
