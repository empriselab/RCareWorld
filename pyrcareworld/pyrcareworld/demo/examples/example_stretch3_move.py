from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

env = RCareWorld(executable_file="/home/cathy/Workspace/rcareworld_new/RCareUnity/Build/TestPlayer.x86_64", assets=["stretch-3"])

stretch = env.InstanceObject(name="stretch-3", attr_type=attr.ControllerAttr)
stretch.SetTransform(position=[0, 0.05, 0])
stretch.SetImmovable(False)
env.step()

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

while 1:
    stretch.TurnLeft(90, 30)
    env.step(300)
