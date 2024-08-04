import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# Initialize the environment with the specified assets
env = RCareWorld(assets=["Rigidbody_Box", "stretch-3"], executable_file="C:\\Users\\15156\\Desktop\\New folder (2)\\Rcareworld.exe")

print("Environment initialized.")


# Create an instance of a Rigidbody_Box and set its position
box = env.InstanceObject(name="Rigidbody_Box", id=123456, attr_type=attr.RigidbodyAttr)
box.SetTransform(position=[0.5, 0.2, 0.5], scale=[0.05, 0.05, 0.05])
env.step(5)
print("Box created.")

box.SetTransform(
    position=[0.5, 0.2, 0.5], 
    scale=[0.05, 0.05, 0.05],
    rotation=[0, 0, 0],
    )
env.step(100)

# Print the data attributes of the box
print("Rigidbody_Box Data:")
for key in box.data:
    print(f"{key}: {box.data[key]}")

# Create an instance of the Stretch robot and set its initial properties
stretch = env.InstanceObject(name="stretch-3", id=789789, attr_type=attr.ControllerAttr)
stretch.SetTransform(position=[0, 0.05, 0])
stretch.SetImmovable(False)
env.step()
gripper = env.GetAttr(7897890)
gripper.GripperOpen()
env.step()

# Move the robot to the position above the box
stretch.IKTargetDoMove(position=[0.5, 0.3, 0.5], duration=3, speed_based=False)
stretch.WaitDo()

# Move the robot down to grasp the box
stretch.IKTargetDoMove(position=[0.5, 0.05, 0.5], duration=2, speed_based=False)
stretch.WaitDo()
gripper.GripperClose()
env.step(50)

# Lift the box
stretch.IKTargetDoMove(position=[0.5, 0.3, 0.5], duration=3, speed_based=False)
stretch.WaitDo()

# Move the box to a new position
stretch.IKTargetDoMove(position=[0.7, 0.3, 0.5], duration=3, speed_based=False)
stretch.WaitDo()

# Open the gripper to release the box
gripper.GripperOpen()
env.step(50)

# Move the robot back to the initial position
stretch.IKTargetDoMove(position=[0, 0.3, 0], duration=3, speed_based=False)
stretch.WaitDo()

# End the environment session
env.Pend()
env.close()
