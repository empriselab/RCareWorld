print("""
This script demonstrates the setup and interaction of a Digit sensor within the RCareWorld environment.

What it Implements:
- Initializes the environment with a Digit sensor object and a target object.
- Sets the position of both the Digit sensor and the target.
- Configures the camera view for better observation of the interaction.

What the Functionality Covers:
- Understanding how to instantiate and position Digit sensors and targets in RCareWorld.
- Learning how to set the camera view transform to observe specific interactions.

Required Operations:
- Mouse Interaction: The script allows for manual interaction with the Digit sensor by dragging the sphere.
- Waiting: The environment waits for user interaction.

Additional Information:
- The visualization in RGB shows the output of the Digit sensor.
- The red-only visualization might represent the intensity map or another specific channel related to the sensor's output.
""")

import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.digit_attr import DigitAttr
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment
env = RCareWorld(executable_file=player_path)

# Create an instance of a Digit object and set its position
digit = env.InstanceObject(name="Digit", attr_type=DigitAttr)
digit.SetTransform(position=[0, 0.015, 0])

# Create an instance of a target object and set its position
target = env.InstanceObject(name="DigitTarget")
target.SetTransform(position=[0, 0.05, 0.015])

# Set the view transform for the environment
env.SetViewTransform(position=[-0.1, 0.033, 0.014], rotation=[0, 90, 0])

# Perform a simulation step
env.Pend()

# You can then drag the sphere to interact with the digit sensor
# Close the environment
env.close()
