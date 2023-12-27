from pyrcareworld.envs.learning_envs.dressing_env import DressingEnv


__all__ = [
    "LimbRepositioningEnv",
    "BedBathingEnv",
    "FeedingEnv",
    "StretchToiletingEnv",
    "KinovaAmbulatingEasyEnv",
    "KinovaAmbulatingNormalEnv",
    "KinovaAmbulatingHardEnv",
    "DressingEnv",
]

# Specify the path to the executable file
rcareworld_base_root = "/home/cathy/Workspace/RCareWorld_stable/Build"
try:
    from gym.envs.registration import register

    register(
        id="Dressing-v1",
        entry_point="pyrcareworld.envs.learning_envs:DressingEnv",
        kwargs={
            "executable_file": "/home/cathy/Workspace/rfu_063/Build/Dressing/dressing.x86_64"
        },
    )
    register(
        id="Feeding-v1",
        entry_point="pyrcareworld.envs.learning_envs:FeedingEnv",
        kwargs={
            "executable_file": "/home/cathy/Workspace/rfu_063/Build/Feeding/feeding.x86_64"
        },
    )

except ImportError:
    print("No gym installed. Please install gym!")
    pass
