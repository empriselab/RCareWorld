import os
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "Player/Player.x86_64")

# Supported grippers: allegro_hand_right, bhand, dh_robotics_ag95_gripper, franka_hand, svh
# Initialize the environment with the specified gripper
env = RCareWorld(assets=["allegro_hand_right"], executable_file=player_path)

# Create an instance of the Allegro Hand Right gripper
bhand = env.InstanceObject("allegro_hand_right", attr_type=attr.ControllerAttr)
env.step(5)

# Get the number of moveable joints in the gripper
moveable_joint_count = bhand.data["number_of_moveable_joints"]
print(f"moveable_joint_count: {moveable_joint_count}")

# Set the position of all moveable joints to 30 degrees
bhand.SetJointPositionDirectly([30 for _ in range(moveable_joint_count)])
env.step(5)

# Export the gripper's mesh as an OBJ file
output_path = os.path.abspath("./gripper_mesh.obj")
env.ExportOBJ([bhand.id], output_path)
print(f"Gripper mesh exported to {output_path}")

# End the environment session
env.Pend()
env.close()
