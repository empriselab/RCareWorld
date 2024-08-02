import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes import ClothAttr, ControllerAttr
from pyrcareworld.demo import mesh_path

# Initialize the environment
env = RCareWorld()
env.DebugObjectPose()
env.EnabledGroundObiCollider(True)

# Load the T-shirt mesh
t_shirt_path = os.path.join(mesh_path, 'Tshirt.obj')
mesh = env.LoadCloth(path=t_shirt_path, id=123)
mesh.SetTransform(position=[0, 1, 0])

# Perform initial simulation steps to stabilize the cloth
env.step(200)

# Get particles data from the mesh
mesh.GetParticles()
env.step()
print(mesh.data)

# Extract positions of specific particles
position1 = mesh.data['particles'][500]
position2 = mesh.data['particles'][200]

# Create an instance of the robot object
robot_id = 456
robot = env.InstanceObject(name="kinova_gen3_robotiq85", id=robot_id, attr_type=ControllerAttr)
robot.SetPosition([0, 0, 0])
env.step()

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(robot_id)
gripper.GripperOpen()

# Move and rotate the robot to the initial position
robot.IKTargetDoMove(position=[0, 1, 0.5], duration=2, speed_based=False)
robot.IKTargetDoRotate(rotation=[0, 0, 180], duration=2, speed_based=False)
robot.WaitDo()

# Attach the cloth to the robot gripper
mesh.AddAttach(robot_id, max_dis=0.04)
env.step()

# Simulate grasping
gripper.GripperClose()
env.step()

# Move the robot with the cloth
robot.IKTargetDoMove(position=[0, 1, 1], duration=2, speed_based=False)
robot.WaitDo()

# Open the gripper to release the cloth
gripper.GripperOpen()
env.step()

# Remove the attachment
mesh.RemoveAttach(robot_id)
env.step()

# Close the environment
env.close()
