from abc import ABC

import pyrcareworld
from pyrcareworld.agents.cloth import Cloth
from pyrcareworld.agents.rope import Rope
from pyrcareworld.environment import UnityEnvironment
from pyrcareworld.side_channel.environment_parameters_channel import (
    EnvironmentParametersChannel,
)
from pyrcareworld.rfuniverse_channel import AssetChannel
from pyrcareworld.rfuniverse_channel import InstanceChannel
from pyrcareworld.rfuniverse_channel import DebugChannel
import gymnasium as gym
from gymnasium.utils import seeding
import os

from pyrcareworld.agents import Robot
from pyrcareworld.agents import Human
from pyrcareworld.objects import RCareWorldBaseObject
from pyrcareworld.sensors import Camera
from pyrcareworld.sensors import Skin


def select_available_worker_id():
    if not os.path.exists(pyrcareworld.user_path):
        os.makedirs(pyrcareworld.user_path)
    log_file = os.path.join(pyrcareworld.user_path, "worker_id_log")

    worker_id = 1
    worker_id_in_use = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            worker_ids = f.readlines()
            for line in worker_ids:
                worker_id_in_use.append(int(line))
        while worker_id in worker_id_in_use:
            worker_id += 1

    worker_id_in_use.append(worker_id)
    with open(log_file, "w") as f:
        for id in worker_id_in_use:
            f.write(str(id) + "\n")

    return worker_id


def delete_worker_id(worker_id):
    log_file = os.path.join(pyrcareworld.user_path, "worker_id_log")

    worker_id_in_use = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            worker_ids = f.readlines()
            for line in worker_ids:
                worker_id_in_use.append(int(line))

    worker_id_in_use.remove(worker_id)
    with open(log_file, "w") as f:
        for id in worker_id_in_use:
            f.write(str(id) + "\n")


class RCareWorldBaseEnv(ABC):
    """
    This class is the base class for RCareWorld environments. In RCareWorld, every environment will be
    packaged in the Gym-like environment class. For custom environments, users will have to implement
    step(), reset(), seed(), _get_obs(). This idea follows the 0.6.3 version of RFUniverse.
    """

    metadata = {"render.modes": ["human", "rgb_array"]}
    rcareworld_channel_ids = {
        "instance_channel": "09bfcf57-9120-43dc-99f8-abeeec59df0f",
        "asset_channel": "d587efc8-9eb7-11ec-802a-18c04d443e7d",
        "debug_channel": "02ac5776-6a7c-54e4-011d-b4c4723831c9",
    }

    def __init__(
        self,
        executable_file: str = None,
        scene_file: str = None,
        custom_channels: list = [],
        assets: list = [],
        graphics: bool = True,
        **kwargs
    ):
        # time step
        self.t = 0
        self.worker_id = select_available_worker_id()
        # initialize RCareWorld channels
        self.channels = custom_channels.copy()
        self._init_channels(kwargs)
        self.assets = assets
        # initialize environment
        self.executable_file = executable_file
        self.scene_file = scene_file
        self.graphics = graphics
        self._init_env()

    def _init_env(self):
        if str(self.executable_file).lower() == "@editor":
            self.env = UnityEnvironment(
                worker_id=0,
                side_channels=self.channels,
                no_graphics=not self.graphics,
            )
        elif self.executable_file is not None:
            self.env = UnityEnvironment(
                worker_id=self.worker_id,
                file_name=self.executable_file,
                side_channels=self.channels,
                no_graphics=not self.graphics,
            )
        elif os.path.exists(pyrcareworld.executable_file):
            self.env = UnityEnvironment(
                worker_id=self.worker_id,
                file_name=pyrcareworld.executable_file,
                side_channels=self.channels,
                no_graphics=not self.graphics,
            )
        else:
            self.env = UnityEnvironment(
                worker_id=0,
                side_channels=self.channels,
                no_graphics=not self.graphics,
            )

        if self.scene_file is not None:
            self.asset_channel.LoadSceneAsync(self.scene_file)
            self.asset_channel.data["load_done"] = False
            while not self.asset_channel.data["load_done"]:
                self._step()
        if len(self.assets) > 0:
            self.asset_channel.PreLoadAssetsAsync(self.assets)
            self.asset_channel.data["load_done"] = False
            while not self.asset_channel.data["load_done"]:
                self._step()
        self.env.reset()

    def _init_channels(self, kwargs: dict):
        # Compulsory channels
        # Environment parameters channel
        self.env_param_channel = EnvironmentParametersChannel()
        self.channels.append(self.env_param_channel)
        # Asset channel
        self.asset_channel = AssetChannel(self.rcareworld_channel_ids["asset_channel"])
        self.instance_channel = InstanceChannel(
            self.rcareworld_channel_ids["instance_channel"]
        )
        self.debug_channel = DebugChannel(self.rcareworld_channel_ids["debug_channel"])
        self.channels.append(self.asset_channel)
        self.channels.append(self.instance_channel)
        self.channels.append(self.debug_channel)

    def _step(self):
        self.env.step()

    def step(self):
        self.env.step()

    # def render(
    #         self,
    #         id,
    #         mode='human',
    #         width=512,
    #         height=512,
    #         target_position=None,
    #         target_euler_angles=None
    # ):
    #     """
    #     Render an image with given resolution, target position and target euler angles.
    #     TODO: Current version only support RoboTube, which only needs RGB image. For depth, normal, ins_seg, optical
    #         flow, etc., please refer to `camera_channel.py` for more actions.
    #
    #     Args:
    #         id: Int. Camera ID.
    #         mode: Str. OpenAI-Gym style mode.
    #         width: Int. Optional. The width of target image.
    #         height: Int. Optional. The height of target image.
    #         target_position: List. Optional. The target position of this camera, in [X, Y, Z] order.
    #         target_euler_angles: List. Optional. The target euler angles of this camera, in [X, Y, Z] order.
    #             Each element is in degree, not radius.
    #
    #     Returns:
    #         A numpy array with size (width, height, 3). Each pixel is in [R, G, B] order.
    #     """
    #     assert self.camera_channel is not None, \
    #         'There is no camera available in this scene. Please check.'
    #
    #     target_position = list(target_position) if target_position is not None else None
    #     target_euler_angles = list(target_euler_angles) if target_euler_angles is not None else None
    #     '''
    #     self.camera_channel.set_action(
    #         'SetTransform',
    #         id=id,
    #         position=target_position,
    #         rotation=target_euler_angles,
    #     )'''
    #     #self._step()
    #
    #     self.camera_channel.set_action(
    #         'GetImages',
    #         rendering_params=[[id, width, height]]
    #     )
    #     self._step()
    #
    #     img = self.camera_channel.images.pop(0)
    #     return img

    def close(self):
        delete_worker_id(self.worker_id)
        self.env.close()


class RCareWorldGymWrapper(RCareWorldBaseEnv, gym.Env):
    def __init__(
        self,
        executable_file: str = None,
        scene_file: str = None,
        custom_channels: list = [],
        assets: list = [],
        **kwargs
    ):
        RCareWorldBaseEnv.__init__(
            self,
            executable_file=executable_file,
            scene_file=scene_file,
            custom_channels=custom_channels,
            assets=assets,
            **kwargs,
        )

    def close(self):
        RCareWorldBaseEnv.close(self)


# class RCareWorldGymGoalWrapper(gym.GoalEnv, RCareWorldBaseEnv):
#     def __init__(
#         self,
#         executable_file: str = None,
#         scene_file: str = None,
#         custom_channels: list = [],
#         assets: list = [],
#         **kwargs
#     ):
#         RCareWorldBaseEnv.__init__(
#             self,
#             executable_file=executable_file,
#             scene_file=scene_file,
#             custom_channels=custom_channels,
#             assets=assets,
#             **kwargs,
#         )

#     def reset(self):
#         gym.GoalEnv.reset(self)

#     def close(self):
#         RCareWorldBaseEnv.close(self)


class RCareWorld(RCareWorldBaseEnv):
    def __init__(
        self,
        executable_file: str = None,
        scene_file: str = None,
        custom_channels: list = [],
        assets: list = [],
        **kwargs
    ):
        super().__init__(
            executable_file=executable_file,
            scene_file=scene_file,
            custom_channels=custom_channels,
            assets=assets,
            **kwargs,
        )
        self.robot_dict = {}
        self.rope_dict = {}
        self.object_dict = {}
        self.cloth_dict = {}
        self.camera_dict = {}
        self.human_dict = {}
        self.lighting_dict = {}
        self.sensor_dict = {}
        self._step()

    def create_robot(
        self,
        id: int,
        gripper_list: list = None,
        robot_name: str = None,
        urdf_path: str = None,
        base_pos: list = [0, 0, 0],
        base_orn=[-0.707107, -0.707107, -0.707107, 0.707107],
    ) -> Robot:
        """
        Create a robot in the scene
        :param id: robot id
        :param gripper_list: list of gripper ids
        :param robot_type: robot type, str, check robot.py
        :param urdf_path: path to urdf file, needed if robot_type is None
        :param base_pos: base position of the robot (x, y, z) same as unity
        :param base_orn: base orientation of the robot (x, y, z) same as unity
        """
        if urdf_path is None:
            self.robot_dict[id] = Robot(
                self,
                id=id,
                gripper_id=gripper_list,
                robot_name=robot_name,
                base_pose=base_pos,
                base_orientation=base_orn,
            )
        else:
            self.robot_dict[id] = Robot(
                self,
                id=id,
                gripper_id=gripper_list,
                urdf_path=urdf_path,
                base_pose=base_pos,
                base_orientation=base_orn,
            )
        this_robot = self.robot_dict[id]
        return this_robot

    def create_object(
        self, id: int, name: str, is_in_scene: bool
    ) -> RCareWorldBaseObject:
        """create object

        Args:
            id (int): id for the object
            name (str): name for the addressable/object
            is_in_scene (bool): whether the object is in the scene

        Returns:
            The object class
        """
        self.object_dict[id] = RCareWorldBaseObject(self, id, name, is_in_scene)
        this_object = self.object_dict[id]
        return this_object

    def create_human(self, id: int, name: str, is_in_scene: bool) -> Human:
        """create human

        Args:
            id (int): id for the human
            name (str): name for the addressable/human
            is_in_scene (bool): whether the human is in the scene

        Returns:
            The human class
        """
        self.human_dict[id] = Human(self, id, name, is_in_scene)
        this_human = self.human_dict[id]
        return this_human

    def create_cloth(self, id: int, name: str, is_in_scene: bool) -> Cloth:
        """
        Creates a cloth object in the scene.

        Args:
            id: Int. The ID of the cloth object.
            name: Str. The name of the cloth object.
            is_in_scene: Bool. Whether the cloth object is in the scene.

        Returns:
            The cloth Object.
        """
        self.cloth_dict[id] = Cloth(self, id, name, is_in_scene)
        this_cloth = self.cloth_dict[id]
        return this_cloth
    
    def create_rope(self, id: int, name: str, is_in_scene: bool) -> Cloth:
        """
        Creates a rope object in the scene.

        Args:
            id: Int. The ID of the rope object.
            name: Str. The name of the rope object.
            is_in_scene: Bool. Whether the rope object is in the scene.

        Returns:
            The rope Object.
        """
        self.rope_dict[id] = Rope(self, id, name, is_in_scene)
        this_rope = self.rope_dict[id]
        return this_rope

    def create_skin(self, id: int, name: str, is_in_scene: bool) -> Skin:
        """create skin

        Args:
            id (int): id for the skin
            name (str): name for the addressable/skin
            is_in_scene (bool): whether the skin is in the scene

        Returns:
            The skin class
        """
        self.skin = Skin(self, id, name, is_in_scene)
        return self.skin

    def create_camera(
        self,
        id: int,
        name: str,
        intrinsic_matrix: list = [600, 0, 0, 0, 600, 0, 240, 240, 1],
        width: int = 480,
        height: int = 480,
        fov: float = 60,
        is_in_scene: bool = False,
    ) -> Camera:
        """create camera

        Args:
            id (int): id for the camera
            name (str): name for the addressable/camera
            is_in_scene (bool): whether the camera is in the scene

        Returns:
            The camera class
        """
        self.camera_dict[id] = Camera(
            self, id, name, intrinsic_matrix, width, height, fov, is_in_scene
        )
        this_camera = self.camera_dict[id]
        return this_camera

    def close(self):
        """close the environment"""
        super().close()

    def ignoreLayerCollision(self, layer1: int, layer2: int, ignore: bool):
        """ignore the collision between two layers

        Args:
            layer1 (int): id of the layer
            layer2 (int): id of the layer
            ignore (bool): id of the layer
        """
        self.asset_channel.set_action(
            "IgnoreLayerCollision",
            layer1=layer1,
            layer2=layer2,
            ignore=ignore,
        )

    def getCurrentCollisionPairs(self):
        """get current collision pairs"""
        self.asset_channel.set_action("GetCurrentCollisionPairs")
        self._step()
        result = self.asset_channel.data["collision_pairs"]
        return result

    def setGravity(self, x: float, y: float, z: float):
        """Set global environment

        Args:
            x (float): gravity in x direction
            y (float): gravity in y direction
            z (float): gravity in z direction
        """
        self.asset_channel.set_action(
            "SetGravity",
            x=x,
            y=y,
            z=z,
        )

    def setGroundPhysicMaterial(
        self,
        bounciness: float = 0,
        dynamic_friction: float = 1,
        static_friction: float = 1,
        friction_combine: int = 0,
        bounce_combine: int = 0,
    ):
        """set the physics material for the ground

        Args:
            bounciness (float, optional): How bouncy is the surface? A value of 0 will not bounce.
            A value of 1 will bounce without any loss of energy, certain approximationsare to be expected though
            that might add small amounts of energy to the simulation. Defaults to 0.

            dynamic_friction (float, optional): The friction used when already moving. Usually a value
            from 0 to 1. A value of zero feels like ice, a value of 1 will make it come to rest very quickly
            unless a lot of force or gravity pushes the object. Defaults to 1.

            static_friction (float, optional): he friction used when an object is laying still on a surface.
            Usually a value from 0 to 1. A value of zero feels like ice, a value of 1 will make it very hard to get the
            object moving. Defaults to 1.

            friction_combine (int, optional): How the friction of two colliding objects is combined. Defaults to 0.

            bounce_combine (int, optional): How the bounciness of two colliding objects is combined.
            It has the same modes as Friction Combine Mode. Defaults to 0.
        """
        self.asset_channel.set_action(
            "SetGroundPhysicMaterial",
            bounciness=bounciness,
            dynamic_friction=dynamic_friction,
            static_friction=static_friction,
            friction_combine=friction_combine,
            bounce_combine=bounce_combine,
        )

    def setTimeScale(self, time_scale: float):
        """Set time step

        Args:
            time_scale (float): time step
        """
        self.asset_channel.set_action("SetTimeScale", time_scale=time_scale)

    def stepSeveralSteps(self, steps: int):
        """Run several self._step

        Args:
            steps (int): number of steps
        """
        for i in range(steps):
            self._step()

    def debugObjectPose(self):
        """Visualize object pose"""
        self.debug_channel.set_action(
            "DebugObjectPose",
        )
        self._step()

    def debugObjectID(self):
        """Visualize object ID"""
        self.debug_channel.set_action(
            "DebugObjectID",
        )
        self._step()


class RCareWorldGymWrapper(RCareWorld, gym.Env):
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

    def reset(self):
        gym.GoalEnv.reset(self)

    def close(self):
        super().close()

    def seed(self, seed=1234):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


if __name__ == "__main__":
    env = RCareWorld(executable_file="@Editor")
