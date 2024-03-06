from pyrcareworld.envs.rcareworld_env import RCareWorldBaseEnv
import pyrcareworld.utils.utility as utility
import os

env = RCareWorldBaseEnv()
env._step()
robot_id = 639787
env.asset_channel.set_action(
    "LoadURDF",
    id=robot_id,
    path=os.path.abspath("../URDF/UR5/ur5_robot.urdf"),
    native_ik=True,
)
env.instance_channel.set_action("SetTransform", id=robot_id, position=[1, 0, 0])
env.asset_channel.set_action(
    "LoadURDF",
    id=358136,
    path=os.path.abspath("../URDF/yumi_description/urdf/yumi.urdf"),
    native_ik=False,
)
env.instance_channel.set_action("SetTransform", id=358136, position=[2, 0, 0])
env.asset_channel.set_action(
    "LoadURDF",
    id=985135,
    path=os.path.abspath("../URDF/kinova_gen3/GEN3_URDF_V12.urdf"),
    native_ik=False,
)
env.instance_channel.set_action("SetTransform", id=985135, position=[3, 0, 0])
env.instance_channel.set_action(
    "IKTargetDoMove", id=robot_id, position=[0, 0.5, 0], duration=0.1, relative=True
)
env._step()
while not env.instance_channel.data[robot_id]["move_done"]:
    env._step()
env.instance_channel.set_action(
    "IKTargetDoMove", id=robot_id, position=[0, 0, -0.5], duration=0.1, relative=True
)
env._step()
while not env.instance_channel.data[robot_id]["move_done"]:
    env._step()
env.instance_channel.set_action(
    "IKTargetDoMove", id=robot_id, position=[0, -0.2, 0.3], duration=0.1, relative=True
)
env.instance_channel.set_action(
    "IKTargetDoRotateQuaternion",
    id=robot_id,
    quaternion=utility.UnityEularToQuaternion([0, 90, 0]),
    duration=30,
    relative=True,
)
env._step()
while (
    not env.instance_channel.data[robot_id]["move_done"]
    or not env.instance_channel.data[robot_id]["rotate_done"]
):
    env._step()

while 1:
    env._step()
