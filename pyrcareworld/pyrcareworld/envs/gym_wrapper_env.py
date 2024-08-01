from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
from typing import Any, SupportsFloat

try:
    import gymnasium as gym
except ImportError:
    print("This feature requires gymnasium, please install with `pip install gymnasium`")
    raise


class RCareWorldGymWrapper(RCareWorld, gym.Env):
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
        check_version: bool = True
    ):
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

    def env_step(self, count: int = 1, simulate: bool = True, collect: bool = True):
        """
        Send the messages of called functions to Unity and simulate for a step, then accept the data from Unity.

        :param count: The number of steps for executing Unity simulation.
        :param simulate: Simulate physics.
        :param collect: Collect data.
        """
        self.step(count, simulate, collect)

    def step(self, action: gym.core.ActType) -> tuple[gym.core.ObsType, SupportsFloat, bool, bool, dict[str, Any]]:
        """
        Gym step.

        :param action: Gym action.
        :return: A tuple containing the observation, reward, done flag, info dictionary.
        """
        return super().step(action)

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
