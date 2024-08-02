from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# Initialize the environment with specified assets
env = RCareWorld(assets=["Rigidbody_Box", "franka_panda"])

# Create an instance of a Rigidbody_Box and set its position
box = env.InstanceObject(name="Rigidbody_Box", id=123456, attr_type=attr.RigidbodyAttr)
box.SetTransform(position=[0, 1, 0])
env.step(5)

# Print the data attributes of the box
print("Rigidbody_Box Data:")
for key in box.data:
    print(f"{key}: {box.data[key]}")

# Create an instance of a franka_panda robot and set its position
robot = env.InstanceObject(name="franka_panda", id=789789, attr_type=attr.ControllerAttr)
robot.SetTransform(position=[1, 0, 0])
env.step()

# Print the data attributes of the robot
print("Franka_Panda Robot Data:")
for key in robot.data:
    print(f"{key}: {robot.data[key]}")

# End the environment session
env.Pend()
env.close()
