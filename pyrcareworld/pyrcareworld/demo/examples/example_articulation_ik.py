import os
import sys
import pyrcareworld.utils.rfuniverse_utility as utility

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "Player/Player.x86_64")

env = RCareWorld(scene_file="ArticulationIK.json", executable_file=player_path)

# List of robot IDs to be controlled
ids = [221584]

# Function to perform movement and rotation on a robot
def move_and_rotate_robot(robot_id):
    # Get the current robot's attributes
    current_robot = env.GetAttr(robot_id)

    # Move the robot down
    current_robot.IKTargetDoMove(position=[0, 0, -0.5], duration=0.1, relative=True)
    env.step()
    while not current_robot.data["move_done"]:
        env.step()

    # Move the robot to the left
    current_robot.IKTargetDoMove(position=[0, -0.5, 0], duration=0.1, relative=True)
    env.step()
    while not current_robot.data["move_done"]:
        env.step()

    # Move the robot up and to the right
    current_robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0.1, relative=True)
    env.step()
    while not current_robot.data["move_done"]:
        env.step()

    # Rotate the robot by 90 degrees around the X-axis
    current_robot.IKTargetDoRotateQuaternion(
        quaternion=utility.UnityEulerToQuaternion([90, 0, 0]),
        duration=0.1,  # Shortened duration to match the movement steps
        relative=True,
    )
    env.step()
    while not current_robot.data["rotate_done"]:
        env.step()

# Perform the operations on each robot in the list
for id in ids:
    move_and_rotate_robot(id)

# Close the environment after all operations are done
env.Pend()
env.close()
