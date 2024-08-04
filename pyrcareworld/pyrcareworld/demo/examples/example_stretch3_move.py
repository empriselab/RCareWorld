from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import time

# Initialize the environment with the specified asset
env = RCareWorld(assets=["stretch_3"], executable_file="C:\\Users\\15156\\Desktop\\New folder (2)\\Rcareworld.exe")
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
