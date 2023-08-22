from pyrfuniverse.envs import RFUniverseBaseEnv
from pyrcareworld.agents import Robot
from pyrcareworld.agents import Human
from pyrcareworld.objects import RCareWorldBaseObject
from pyrcareworld.sensors import Camera
from pyrcareworld.sensors import Skin
import gym
from gym.utils import seeding


class RCareWorld(RFUniverseBaseEnv):
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
        self.object_dict = {}
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
    ) -> None:
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

    def create_object(self, id: int, name: str, is_in_scene: bool):
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

    def create_human(self, id: int, name: str, is_in_scene: bool):
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

    def create_skin(self, id: int, name: str, is_in_scene: bool):
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
    ):
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
