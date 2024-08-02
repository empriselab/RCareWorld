import os
import sys
import time
import random

# 添加项目目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# 初始化环境
env = RCareWorld()
env.SetTimeStep(0.005)

robot_id = 456
robot = env.InstanceObject(name="kinova_gen3_robotiq85", id=robot_id, attr_type=attr.ControllerAttr)
robot.SetPosition([0, 0, 0])
env.step()

gripper = env.GetAttr(robot_id)
gripper.GripperOpen()
env.step()

robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=2, speed_based=False)
robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=2, speed_based=False)
robot.WaitDo()

sponge_id = 123
sponge = env.InstanceObject(name="Rigidbody_Sponge", id=sponge_id, attr_type=attr.RigidbodyAttr)
sponge.SetTransform(
    position=[random.uniform(-0.3, 0.3), 0.03, random.uniform(0.3, 0.5)],
    scale=[0.1, 0.1, 0.1],
)
env.step()

sponge_position = sponge.data["position"]

robot.IKTargetDoMove(
    position=[sponge_position[0], sponge_position[1] + 0.1, sponge_position[2]],
    duration=2,
    speed_based=False,
)
robot.WaitDo()
robot.IKTargetDoMove(
    position=[sponge_position[0], sponge_position[1], sponge_position[2]],
    duration=2,
    speed_based=False,
)
robot.WaitDo()
gripper.GripperClose()
env.step()

robot.IKTargetDoMove(
    position=[0, 0.5, 0],
    duration=2,
    speed_based=False,
    relative=True
)
robot.WaitDo()

gripper.GripperOpen()
env.step()

env.close()
