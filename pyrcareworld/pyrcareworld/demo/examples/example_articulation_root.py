print("""
This script demonstrates the initialization and control of a shadow hand object in the RCareWorld environment.

What it Implements:
- Initializes the environment using a specified executable file.
- Instantiates a shadow hand object with a 6DOF (6 Degrees of Freedom) controller.
- Sets the position of the shadow hand and configures joint stiffness and damping.
- Simulates joint movements with delays between each step.

What the Functionality Covers:
- How to instantiate and manipulate objects in the RCareWorld environment.
- Understanding joint control, including stiffness, damping, and movement.

Required Operations:
- Waiting: The script involves waiting between each joint position update.
- Loop: Iterates over joint positions to update them with delays.
""")

import os
import sys
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment
env = RCareWorld(executable_file=player_path)

# Instantiate the shadow hand object with a controller attribute
shadow = env.InstanceObject("shadowhand", attr_type=attr.ControllerAttr)

# Set the position of the shadow hand
shadow.SetPosition([0, 1, 0])

# Add a 6DOF root to the shadow hand
root = shadow.AddRoot6DOF()

# Perform a simulation step to update the environment
env.step()

# Set joint stiffness and damping for the root
root.SetJointStiffness([100] * 6)
root.SetJointDamping([50] * 6)

# Function to set joint positions with a delay between each step
def set_joint_positions_with_delay(root, positions, delay_steps):
    for index, position in positions:
        root.SetIndexJointPosition(index, position)
        env.step(delay_steps)

# Define joint positions and delays
joint_positions = [
    (0, 0.5),
    (1, 0.5),
    (2, 0.5),
    (3, 45),
    (4, 45),
    (5, 45)
]
delay_steps = 50

# Set the joint positions with delays
set_joint_positions_with_delay(root, joint_positions, delay_steps)

# Close the environment
env.Pend()
env.close()
