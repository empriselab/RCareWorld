import random
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# Initialize the environment with the specified assets and set the time step
env = RCareWorld(assets=["franka_panda"])
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
