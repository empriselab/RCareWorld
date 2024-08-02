import numpy as np
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

env = RCareWorld(assets=["franka_panda"])
env.DebugObjectPose()
env.SetTimeStep(0.005)
robot = env.InstanceObject(name="franka_panda", id=123456, attr_type=attr.ControllerAttr)

robot.SetIKTargetOffset(position=[0, 0.105, 0])
env.step()
robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0, speed_based=False)
robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
robot.WaitDo()

env.step(100)
mass_point = env.InstanceObject(name="MassPoint", id=999, attr_type=attr.RigidbodyAttr)
robot.GetJointWorldPointFromLocal(8, [0, 0, 0])
env.step(simulate=False)
mass_point.SetPosition(robot.data["result_joint_world_point"])
mass_point.Link(robot.id, 8)


last_velocity = [0,0,0]
while 1:
    env.step()
    acc = np.array((mass_point.data["velocity"]) - np.array(last_velocity)) / env.data["fixed_delta_time"]
    print(np.linalg.norm(acc))
    last_velocity = mass_point.data["velocity"]

    if robot.data["move_done"]:
        vector = np.random.rand(3)
        vector /= np.linalg.norm(vector)
        vector *= np.random.uniform(-0.1, 0.1)
        robot.IKTargetDoMove(position=vector.tolist(), duration=0.1, speed_based=True, relative=True)

