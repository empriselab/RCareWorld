import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.humanbody_attr import HumanbodyAttr
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with the specified scene file
env = RCareWorld(scene_file="HumanBodyIK.json", executable_file=player_path)

# Perform an initial simulation step
env.step()

# Print a message explaining the purpose of the example
print("This example shows how BioIK works on the human body. It does not show the range of motion of the careavatar with c6-c7 spinal cord injury.")

# Get the human attribute by ID
human = env.GetAttr(168242)

# Function to perform a series of IK movements
def perform_ik_movements(human, index):
    positions = [
        [0, 0, 0.5],
        [0, 0.5, 0],
        [0, 0, -0.5],
        [0, -0.5, 0]
    ]
    for position in positions:
        human.HumanIKTargetDoMove(index=index, position=position, duration=1, speed_based=False, relative=True)
        human.WaitDo()

# Perform IK movements for specified indices
for index in range(5):
    perform_ik_movements(human, index)

# Close the environment
env.Pend()
env.close()
