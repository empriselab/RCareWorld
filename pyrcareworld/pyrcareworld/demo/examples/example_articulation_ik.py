from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.utils.rfuniverse_utility as utility

env = RCareWorld(scene_file="ArticulationIK.json")
ids = [221584]

for id in ids:
    current_robot = env.GetAttr(id)
    current_robot.IKTargetDoMove(position=[0, 0, -0.5], duration=0.1, relative=True)
    env.step()
    while not current_robot.data["move_done"]:
        env.step()
    current_robot.IKTargetDoMove(position=[0, -0.5, 0], duration=0.1, relative=True)
    env.step()
    while not current_robot.data["move_done"]:
        env.step()
    current_robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0.1, relative=True)
    current_robot.IKTargetDoRotateQuaternion(
        quaternion=utility.UnityEulerToQuaternion([90, 0, 0]),
        duration=30,
        relative=True,
    )
    env.step()
    while not current_robot.data["move_done"] or not current_robot.data["rotate_done"]:
        env.step()

env.Pend()
env.close()
