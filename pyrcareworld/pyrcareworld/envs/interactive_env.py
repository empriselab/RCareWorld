from pyrcareworld.envs import RCareWorld
import numpy as np
import pybullet as p
import math


class InteractiveEnv(RCareWorld):
    def __init__(
        self,
        executable_file: str = None,
        scene_file: str = None,
        custom_channels: list = [],
        assets: list = [],
        **kwargs
    ):
        RCareWorld.__init__(
            self,
            executable_file=executable_file,
            scene_file=scene_file,
            custom_channels=custom_channels,
            assets=assets,
            **kwargs,
        )

        self.robot = self.create_robot(315893, [3158930], "kinova_gen3_7dof")
        self.init_pose_obj = self.create_object(6666, "Ini", True)
        ini_world_pose = self.init_pose_obj.getPosition()
        # self.eef_orn = p.getQuaternionFromEuler([0, math.pi / 2., 0.])
        ini_world_rot = self.init_pose_obj.getQuaternion()
        self.robot.moveTo(ini_world_pose, ini_world_rot)
        self.robot.closeGripper()
        self.skin = self.create_skin(id=114514, name="Skin", is_in_scene=True)

    def step(self):
        pose = self.init_pose_obj.getPosition()
        rot = self.init_pose_obj.getQuaternion()
        self.robot.moveTo(pose, rot)
        skin_info = self.skin.getInfo()
        print(skin_info)
        self._step()

    def demo(self):
        for i in range(10000000):
            self.step()


if __name__ == "__main__":
    env = InteractiveEnv()
    for i in range(10000000):
        env.step()
