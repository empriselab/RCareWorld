from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
from typing import Any, SupportsFloat
import numpy as np
from omegaconf import OmegaConf
import os 

try:
    import gym
    from gym import spaces
except ImportError:
    # fallback only if gym is truly unavailable
    import gymnasium as gym
    from gymnasium import spaces



class RCareWorldWrapper(RCareWorld, gym.Env):
    """
    RCareWorld base environment with Gym class.

    :param executable_file: Str, the absolute path of Unity executable file. None for the last used executable file; "@editor" for using Unity Editor.
    :param scene_file: Str, the absolute path of Unity scene JSON file. All JSON files are located at `<PlayerName>_Data/StreamingAssets/SceneData` by default. This is located in the build for the executable files.
    :param assets: List, the list of pre-loaded assets. All assets in the list will be pre-loaded in Unity when the environment is initialized, which will save time during instantiating.
    :param graphics: Bool, True for showing GUI and False for headless mode.
    :param port: Int, the port for communication.
    :param proc_id: Int, the process id for the Unity environment. 0 for the first process, 1 for the second process, and so on.
    :param log_level: Int, the log level for Unity environment. 0 for no log, 1 for error logs, 2 for warnings and errors, 3 for all logs.
    :param ext_attr: (Deprecated in RCareWorld 1.5.0) List, the list of extended attributes. All extended attributes will be added to the environment.
    :param check_version: Bool, True for checking the version of the Unity environment and the pyrcareworld library. False for not checking the version.
    """

    def __init__(
        self,
        executable_file: str = None,
        scene_file: str = None,
        assets: list = [],
        graphics: bool = True,
        port: int = 5004,
        proc_id=0,
        log_level=0,
        ext_attr: list[type(attr.BaseAttr)] = [],
        check_version: bool = True,
        shape_meta: dict = None,
        robot_id: int = 315893,
        target_id: int = 7654,
        camera_id: list[int] = [2333, 6700],
        manipulated_object_id: list = [7890],
        object_id: int = 7890,
        image_shape=(3, 512, 512),
        seed: int = 42
    ):
        # Ensure unique port assignment
        if proc_id > 0:
            port = port + proc_id
        
        # Additional check: find an available port if the specified one is in use
        import socket
        original_port = port
        max_attempts = 100
        for attempt in range(max_attempts):
            try:
                # Test if port is available
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind(("localhost", port))
                test_socket.close()
                break  # Port is available
            except OSError:
                # Port is in use, try next one
                port += 1
                if attempt == max_attempts - 1:
                    raise RuntimeError(f"Could not find available port after {max_attempts} attempts starting from {original_port}")
        
        super().__init__(
            executable_file=executable_file,
            scene_file=scene_file,
            assets=assets,
            graphics=graphics,
            port=port,
            proc_id=proc_id,
            log_level=log_level,
            ext_attr=ext_attr,
            check_version=check_version
        )
        #breakpoint()
        #Set Unity id attributes
        self.robot = self.GetAttr(robot_id)
        # Create target object
        self.target = self.GetAttr(target_id)

        # Create manipulated object
        self.object = self.GetAttr(object_id)
        if len(camera_id) ==1:
            self.camera = self.GetAttr(camera_id[0])
        elif len(camera_id) == 2:
            #self.wrist_cam = self.env.GetAttr(self.camera_id[0])
            self.topdown_cam = self.GetAttr(camera_id[1])
        else:
            raise ValueError("camera_id must be a list of length 1 or 2")

        cfg_path = os.path.expanduser('/home/sarah/projects/RCareWorld/pyrcareworld/pyrcareworld/constrained-dp/diffusion_policy/new_image_pusht_cnn.yaml')
        cfg = OmegaConf.load(cfg_path)
        shape_meta = cfg['shape_meta']
        
        action_shape = shape_meta['action']['shape']
        #TODO This is arbitrary may need to modify later
        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=action_shape, dtype=np.float32)
        
        obs_space = {}
        for key, spec in shape_meta["obs"].items():
            shape = tuple(spec["shape"])
            # follow the same convention used in RobomimicImageWrapper
            if key.endswith("image"):
                low, high = 0.0, 1.0
            elif key.endswith(("quat", "qpos", "pos")) or spec.get("type") == "low_dim":
                low, high = -1.0, 1.0
            else:
                raise RuntimeError(f"Unsupported obs key '{key}' in shape_meta.")
            obs_space[key] = spaces.Box(low=low, high=high, shape=shape, dtype=np.float32)
        self.observation_space = spaces.Dict(obs_space)
        
    def set_initial_position(self):
        """Set the initial position of the robot"""
        print("\033[94m" + "Setting initial robot position..." + "\033[0m")
        
        # self.robot.EnabledNativeIK(False)
        self.env.step()
        # Move robot to initial position
        self.robot.IKTargetDoMove(position=[0, 0.14, 0.5], duration=0.5, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 0, 180], duration=0.5, speed_based=False)
        self.robot.WaitDo()
        self.env.step(50)

        # self.robot.EnabledNativeIK(True)
        self.env.step()
        print("\033[94m" + "Robot initial position set." + "\033[0m")


    def step(self, count: int = 1, simulate: bool = True, collect: bool = True):
        """
        Gym step.

        :param action: Gym action.
        :return: A tuple containing the observation, reward, done flag, info dictionary.
        """
        super().step(count, simulate, collect)

        action = np.asarray(action, dtype=np.float32).reshape(-1)
 
        delta = action * 0.02

        # interpret as (dx,dy,dz, dRx,dRy,dRz) deltas on EE target
        cur_pos = np.array(self.robot.data["position"], dtype=np.float32)
        cur_rot = np.array(self.robot.data["rotation"], dtype=np.float32)

        tgt_pos = (cur_pos + delta[:3]).tolist()
        tgt_rot = (cur_rot + delta[3:6]).tolist()

        self.robot.IKTargetDoMove(position=tgt_pos, duration=0.1, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=tgt_rot, duration=0.1, speed_based=False)
        self.robot.WaitDo()

        obs = self._get_obs()
        reward = 0.0
        terminated = False
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info

    def env_close(self):
        """
        Close the environment.
        """
        self.close()

    def close(self):
        """
        Close the Gym environment.
        """
        super().close()
    
def test():
    import os
    from omegaconf import OmegaConf
    cfg_path = os.path.expanduser('/home/sarah/projects/RCareWorld/pyrcareworld/pyrcareworld/constrained-dp/diffusion_policy/new_image_pusht_cnn.yaml')
    cfg = OmegaConf.load(cfg_path)
    shape_meta = cfg['shape_meta']
    from matplotlib import pyplot as plt

    

    wrapper = RCareWorldWrapper(
        shape_meta=shape_meta
    )
    wrapper.seed(0)
    obs = wrapper.reset()
    img = wrapper.render()
    plt.imshow(img)


    # states = list()
    # for _ in range(2):
    #     wrapper.seed(0)
    #     wrapper.reset()
    #     states.append(wrapper.env.get_state()['states'])
    # assert np.allclose(states[0], states[1])

    # img = wrapper.render()
    # plt.imshow(img)
    # wrapper.seed()
    # states.append(wrapper.env.get_state()['states'])
if __name__ == "__main__":
    test()
