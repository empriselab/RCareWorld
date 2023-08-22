import fire
from pyrcareworld.envs import *


def create_environment(
    env_name: str,
    scene_file: str = None,
    executable_file: str = "@Editor",
    assets: list = None,
    custom_channels: list = None,
    user_input: bool = False,
    record: bool = False,
):

    """
    This function creates an instance of the specified environment class
    and then runs its 'demo_env' method.

    Parameters:
    env_name (str): Name of the environment class to instantiate.
    scene_file (str, optional): Path of the scene file to load into the environment.
    executable_file (str, optional): Path of the executable file. Default is '@Editor'.
    assets (list, optional): List of assets to load into the environment. Default is an empty list.
    custom_channels (list, optional): List of custom channels to use in the environment. Default is an empty list.
    user_input (bool, optional): Flag indicating whether the demo_env method is interactive. Default is False.
    record (bool, optional): Flag indicating whether to record the demo. Default is False.

    Returns:
    int: 0, indicating that the function completed successfully.

    Raises:
    ValueError: If the environment class does not exist or if the 'demo_env' method does not exist in the class.
    """

    try:
        env_class = globals()[env_name]
        env = env_class(
            scene_file=scene_file,
            executable_file=executable_file,
            assets=assets if assets else [],
            custom_channels=custom_channels if custom_channels else [],
        )
    except KeyError:
        raise ValueError(
            f"The environment '{env_name}' does not exist or hasn't been imported."
        )

    try:
        env.demo_env(user_input=user_input, record=record)
        # TODO: Add a user_input and record flag to the demo_env method
    except AttributeError:
        raise ValueError(
            f"The class '{env_name}' does not have a 'demo_env' method. Implement it to run a demo."
        )

    return 0


if __name__ == "__main__":
    fire.Fire(create_environment)
