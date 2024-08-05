from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import time

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "Player/Player.x86_64")

# Initialize the environment with the specified asset
env = RCareWorld(assets=["stretch_3"], executable_file=player_path)
env.SetTimeStep(0.005)

print("Environment initialized.")

# Create an instance of the Stretch robot and set its initial properties
stretch = env.InstanceObject(name="stretch-3", id=221582, attr_type=attr.ControllerAttr)


stretch.SetPosition([0, 0, 0])
stretch.SetImmovable(False)
env.step()

print("Stretch robot created.")


time.sleep(10)


gripper = env.GetAttr(2215820)
gripper.GripperOpen()
env.step()

stretch.IKTargetDoMove(position=[0, 0.5, 0.5], duration=3, speed_based=False)
# stretch.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
stretch.WaitDo()

# Uncomment the following block to move and turn the Stretch robot with specific steps
# stretch.MoveForward(1, 0.2)
# env.step(300)
# stretch.TurnLeft(90, 60)
# env.step(300)
# stretch.MoveForward(1, 0.2)
# env.step(300)
# stretch.TurnLeft(90, 30)
# env.step(300)
# stretch.MoveForward(1, 0.2)
# env.step(300)
# stretch.TurnRight(90, 30)
# env.step(300)
# stretch.MoveBack(1, 0.2)
# env.step(300)
# stretch.TurnRight(90, 30)
# env.step(300)
stretch.TurnLeft(90, 30)
env.step(300)
