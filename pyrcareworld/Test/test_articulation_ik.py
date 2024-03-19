from pyrcareworld.envs.rcareworld_env import RCareWorldBaseEnv
import pyrcareworld.utils.utility as utility

env = RCareWorldBaseEnv(
    # scene_file='ArticulationIK.json'
)
env._step()
ids = [639787, 985196, 221584]

for id in ids:
    env.instance_channel.set_action(
        "IKTargetDoMove", id=id, position=[0, 0, -0.5], duration=0.1, relative=True
    )
    env._step()
    while not env.instance_channel.data[id]["move_done"]:
        env._step()
    env.instance_channel.set_action(
        "IKTargetDoMove", id=id, position=[0, -0.5, 0], duration=0.1, relative=True
    )
    env._step()
    while not env.instance_channel.data[id]["move_done"]:
        env._step()
    env.instance_channel.set_action(
        "IKTargetDoMove", id=id, position=[0, 0.5, 0.5], duration=0.1, relative=True
    )
    env.instance_channel.set_action(
        "IKTargetDoRotateQuaternion",
        id=id,
        quaternion=utility.UnityEularToQuaternion([90, 0, 0]),
        duration=30,
        relative=True,
    )
    env._step()
    while (
        not env.instance_channel.data[id]["move_done"]
        or not env.instance_channel.data[id]["rotate_done"]
    ):
        env._step()

while 1:
    env._step()
