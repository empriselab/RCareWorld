from pyrfuniverse.envs import RFUniverseBaseEnv
from pyrcareworld.agents import Robot
from pyrcareworld.agents import Human
from pyrcareworld.objects import RCareWorldBaseObject
from pyrcareworld.sensors import Camera
import gym


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
        self.object_dict= {}
        self.camera_dict = {}
        self.human_dict = {}

    def create_robot(self, id:int, gripper_list:list = None, robot_name:str = None, urdf_path:str = None, base_pos:list = [0, 0, 0], base_orn = [-0.707107, -0.707107, -0.707107, 0.707107]) -> None:
        '''
        Create a robot in the scene
        :param id: robot id
        :param gripper_list: list of gripper ids
        :param robot_type: robot type, str, check robot.py
        :param urdf_path: path to urdf file, needed if robot_type is None
        :param base_pos: base position of the robot (x, y, z) same as unity
        :param base_orn: base orientation of the robot (x, y, z) same as unity
        '''
        if urdf_path is None:
            self.robot_dict[id] = Robot(self, id=id, gripper_id=gripper_list, robot_name=robot_name, base_pose=base_pos, base_orientation=base_orn)
        else:
            self.robot_dict[id] = Robot(self, id=id, gripper_id=gripper_list, urdf_path=urdf_path, base_pose=base_pos, base_orientation=base_orn)

    def create_object(self, id:int, name:str, is_in_scene:bool) -> None:
        self.object_dict[id] = RCareWorldBaseObject(self, id, name, is_in_scene)

    def create_human(self, id:int, name:str, is_in_scene:bool) -> None:
        self.human_dict[id] = Human(self, id, name, is_in_scene)

    def get_human(self, this_id:int):
        human = self.human_dict[this_id]
        return human

    def get_robot(self, this_id:int):
        robot = self.robot_dict[this_id]
        return robot

    def get_object(self, this_id:int):
        this_object = self.object_dict[this_id]
        return this_object

    def create_camera(
                self,
                id:int,
                name:str,
                intrinsic_matrix:list = [600, 0, 0, 0, 600, 0, 240, 240, 1],
                width:int = 480,
                height:int = 480,
                fov:float = 60,
                is_in_scene:bool = False,) -> None:
        self.camera_dict[id] = Camera(self, id, name, intrinsic_matrix, width, height, fov, is_in_scene)

    def get_camera(self, this_id:int):
        camera = self.camera_dict[this_id]
        return camera

    def close(self):
        super().close()

    def ignoreLayerCollision(self, layer1:int, layer2:int, ignore:bool):
        # @Sarah please check this function and see if it needs a _step() function
        # Also for other functions in this file
        self.asset_channel.set_action(
            'IgnoreLayerCollision',
            layer1 = layer1,
            layer2 = layer2,
            ignore = ignore,
        )

    def getCurrentCollisionPairs(self):
        self.asset_channel.set_action(
            'GetCurrentCollisionPairs'
        )
        self._step()
        result = self.asset_channel.data['collision_pairs']
        return result

    def setGravity(self, x:float, y:float, z:float):
        self.asset_channel.set_action(
            'SetGravity',
            x = x,
            y = y,
            z = z,
        )

    def setGroundPhysicMaterial(self, bounciness:float=0, dynamic_friction:float=1, static_friction:float=1, friction_combine:int=0, bounce_combine:int=0):
        self.asset_channel.set_action(
            'SetGroundPhysicMaterial',
            bounciness = bounciness,
            dynamic_friction = dynamic_friction,
            static_friction = static_friction,
            friction_combine = friction_combine,
            bounce_combine = bounce_combine
        )

    def setTimeScale(self, time_scale:float):
        self.asset_channel.set_action(
            'SetTimeScale',
            time_scale = time_scale
        )

    def stepSeveralSteps(self, steps:int):
        for i in range(steps):
            self._step()

    def debugObjectPose(self):
        self.debug_channel.set_action(
            "DebugObjectPose",
        )
        self._step()

    def debugObjectID(self):
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

    # def close(self):
    #     RCareWorld.close(self)
    def close(self):
        super().close()


