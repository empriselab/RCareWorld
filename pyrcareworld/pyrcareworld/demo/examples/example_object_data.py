print("""
This script demonstrates the instantiation and manipulation of a rigid body box and a Franka Panda robot in the RCareWorld environment.

What it Implements:
- Initializes the environment and creates instances of a Rigidbody_Box and a Franka Panda robot. Note that the URDF loader does not render the texture, so while the robot structures and joints are correctly loaded, the visual appearance of the Franka Panda robot may lack textures.
- Sets the position of both objects and prints their data attributes to the console for inspection.

What the Functionality Covers:
- Understanding how to instantiate objects with rigid body and controller attributes in RCareWorld.
- Demonstrates how to access and print the internal data attributes of these objects.

Required Operations:
- Data Inspection: The script prints out the data attributes of the box and robot after they are instantiated and positioned.
""")

import os
import sys
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with specified assets
env = RCareWorld(assets=["Rigidbody_Box", "franka_panda"],executable_file=player_path)

# Create an instance of a Rigidbody_Box and set its position
box = env.InstanceObject(name="Rigidbody_Box", id=123456, attr_type=attr.RigidbodyAttr)
box.SetTransform(position=[0, 1, 0])
env.step(5)

# Print the data attributes of the box
print("Rigidbody_Box Data:")
for key in box.data:
    # print(f"{key}: {box.data[key]}")
    print("Stop printing Rigidbody_Box data for debugging.")

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
