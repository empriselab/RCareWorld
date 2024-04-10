from .object import RCareWorldBaseObject
import numpy as np


class RCareWorldBed(RCareWorldBaseObject):
    """
    A hospital bed in RCareWorld
    """

    def __init__(self, env, id: int, name: str, is_in_scene: bool = False):
        super().__init__(env=env, id=id, name=name, is_in_scene=is_in_scene)

    def setActuationAngle(self, angle, duration=25) -> None:
        """
        @param angle
        @return:
        """
        assert 0 < angle and angle < 180
        x_rot, rot, z_rot = self.getLocalRotation()
        rot = 360 if rot == 0 else rot
        angles = np.linspace(rot, 360 - angle, num=duration)
        for i in range(len(angles)):
            self.env.instance_channel.set_action(
                "SetTransform",
                id=self.id,
                position=self.getLocalPosition(),
                rotation=[x_rot, angles[i], z_rot],
                is_world=False,
            )
            self.env.step()

    def getCurrentAngle(self):
        rot = self.getLocalRotation()[1]
        return 0 if rot == 0 else 360 - rot
