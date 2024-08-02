from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# Initialize the environment with the specified asset
env = RCareWorld(assets=["stretch-3"])

# Create an instance of the Stretch robot and set its initial properties
stretch = env.InstanceObject(name="stretch-3", attr_type=attr.ControllerAttr)
stretch.SetTransform(position=[0, 0.05, 0])
stretch.SetImmovable(False)
env.step()

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

# Main loop to continuously turn the Stretch robot left
while True:
    stretch.TurnLeft(90, 30)
    env.step(300)
