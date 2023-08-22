from pyrcareworld.envs import RCareWorld
import numpy as np
import pybullet as p
import math


class RobotSkinEnv(RCareWorld):
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

        # create robot
        self.robot = self.create_robot(315893, [3158930], "kinova_gen3_7dof")
        # create the object for pose initialization
        self.init_pose_obj = self.create_object(6666, "Ini", True)
        # get the position of the init_pose_obj, and later move the robot to that position
        ini_world_pose = self.init_pose_obj.getPosition()
        # get the rotation of the init_pose_obj, and later move the robot to that position
        ini_world_rot = self.init_pose_obj.getQuaternion()
        # move the robot to the position of the init_pose_obj with its rotation
        self.robot.moveTo(ini_world_pose, ini_world_rot)
        # close gripper
        self.robot.closeGripper()
        # create the skin
        self.skin = self.create_skin(id=114514, name="Skin", is_in_scene=True)

    def step(self):
        # get the position and rotation of the init_pose_obj
        pose = self.init_pose_obj.getPosition()
        rot = self.init_pose_obj.getQuaternion()
        # move the robot to this object
        self.robot.moveTo(pose, rot)
        # get skin reading
        skin_info = self.skin.getInfo()
        # print it
        print(skin_info)
        # use self._step() to send the command to Unity
        self._step()

    def demo(self):
        # keep the simulation running
        for i in range(10000000):
            self.step()


if __name__ == "__main__":
    # create the environment
    env = RobotSkinEnv()
    # run the environment
    env.demo()
