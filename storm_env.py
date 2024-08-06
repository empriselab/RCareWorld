# import some rcareworld modules
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import pyrcareworld.utils.rfuniverse_utility as utility

# import some storm modules


env = RCareWorld()
robot = env.GetAttr(221584)
cube = env.GetAttr(45678)

env.step()

for i in range(5000):
    cube_pos = cube.data["position"]
    cube_rot = cube.data["rotation"]
    # print("position", cube_pos)
    # robot.IKTargetDoMove(position=cube_pos, duration=0.1, relative=False)
    # robot.IKTargetDoComplete()
    robot.SetJointVelocity([0,0,0,0,0,0,0.0])
    # robot.SetJointStiffness([0] * 7)
    # robot.SetJointDamping([10] * 7)
    env.step()
    print(robot.data["joint_velocities"])
    # robot.IKTargetDoRotateQuaternion(
    #     quaternion=utility.UnityEulerToQuaternion([90, 0, 0]),
    #     duration=30,
    #     relative=True,
    # )
    env.step()
    while not robot.data["move_done"]:
        env.step()
