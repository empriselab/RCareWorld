import pybullet as p
import time
import numpy as np


class PoseUtils:
    """
    A simple pose converter between Unity and Bullet
    """

    def __init__(self):
        pass

    def bullet_pos_to_unity_pos(self, pos: list):
        return [-pos[1], pos[2], pos[0]]

    def unity_pos_to_bullet_pos(self, pos: list):
        return [pos[2], -pos[0], pos[1]]

    def bullet_qua_to_unity_qua(self, qua: list):
        return [-qua[1], qua[2], qua[0], -qua[3]]

    def unity_qua_to_bullet_qua(self, qua: list):
        return [qua[2], -qua[0], qua[1], -qua[3]]

    def bullet_scale_to_unity_scale(self, scale: list):
        return [scale[1], scale[2], scale[0]]

    def unity_scale_to_bullet_scale(self, scale: list):
        return [scale[2], scale[0], scale[1]]


if __name__ == "__main__":
    unity_pos = [0.52, 2.28, 0.75]
    unity_qua = [0, 0.258819103, 0, 0.965925813]
    unity_euler = [0, 30, 0]
    unity_sca = [1.0, 2.0, 1.5]

    id_simulator = p.connect(p.GUI)
    p.setTimeStep(0.02)
    pose = PoseUtils()
    box = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=pose.unity_scale_to_bullet_scale(
            (np.array(unity_sca) / 2).tolist()
        ),
    )
    p.createMultiBody(
        baseVisualShapeIndex=box,
        basePosition=pose.unity_pos_to_bullet_pos(unity_pos),
        baseOrientation=pose.unity_qua_to_bullet_qua(unity_qua),
    )

    while 1:
        p.stepSimulation(id_simulator)
        time.sleep(0.02)
