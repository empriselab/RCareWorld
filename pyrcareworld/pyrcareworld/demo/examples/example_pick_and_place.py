print("""
This script demonstrates the control of a Franka Panda robotic arm in the RCareWorld environment, performing a pick-and-place operation with randomly positioned boxes.

What it Implements:
- Initializes the environment with a Franka Panda robot and sets its inverse kinematics (IK) target offset.
- The robot arm performs pick-and-place operations by moving to randomly generated boxes, picking them up, and placing them in new positions.

What the Functionality Covers:
- Understanding how to control a robotic arm using IK in RCareWorld.
- Demonstrates object manipulation, including picking up and placing rigid body boxes with the gripper.

Required Operations:
- Loop: The script continuously performs pick-and-place operations in a loop.
- Object Manipulation: Creates, moves, and destroys rigid body box objects.
- Robot Control: Executes IK movements and gripper operations to complete the task.
""")

import random
import pyrcareworld.attributes as attr
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")


# Initialize the environment with the specified assets and set the time step
env = RCareWorld(assets=["franka_panda"], executable_file=player_path)
env.SetTimeStep(0.005)

# Create an instance of the Franka Panda robot and set its IK target offset
robot = env.InstanceObject(name="franka_panda", id=123456, attr_type=attr.ControllerAttr)
robot.SetIKTargetOffset(position=[0, 0.105, 0])
env.step()

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(1234560)
gripper.GripperOpen()

# Move and rotate the robot to the initial position
robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0, speed_based=False)
robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
robot.WaitDo()

# Main loop to create, move, and manipulate boxes
while True:
    # Create two Rigidbody_Box instances with random positions
    box1 = env.InstanceObject(name="Rigidbody_Box", id=111111, attr_type=attr.RigidbodyAttr)
    box1.SetTransform(
        position=[random.uniform(-0.5, -0.3), 0.03, random.uniform(0.3, 0.5)],
        scale=[0.06, 0.06, 0.06],
    )
    box2 = env.InstanceObject(name="Rigidbody_Box", id=222222, attr_type=attr.RigidbodyAttr)
    box2.SetTransform(
        position=[random.uniform(0.3, 0.5), 0.03, random.uniform(0.3, 0.5)],
        scale=[0.06, 0.06, 0.06],
    )
    env.step(100)

    # Get the positions of the boxes
    position1 = box1.data["position"]
    position2 = box2.data["position"]

    # Move the robot to the first box, pick it up, and move it to the second box's position
    robot.IKTargetDoMove(
        position=[position1[0], position1[1] + 0.5, position1[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position1[0], position1[1], position1[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()
    gripper.GripperClose()
    env.step(50)
    robot.IKTargetDoMove(
        position=[0, 0.5, 0], duration=2, speed_based=False, relative=True
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position2[0], position2[1] + 0.5, position2[2]],
        duration=4,
        speed_based=False,
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position2[0], position2[1] + 0.06, position2[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()
    gripper.GripperOpen()
    env.step(50)
    robot.IKTargetDoMove(
        position=[0, 0.5, 0], duration=2, speed_based=False, relative=True
    )
    robot.WaitDo()
    robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=2, speed_based=False)
    robot.WaitDo()

    # Destroy the boxes and perform a simulation step
    box1.Destroy()
    box2.Destroy()
    env.step()
