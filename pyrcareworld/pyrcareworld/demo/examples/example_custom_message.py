print("""
This script demonstrates the use of custom attributes and dynamic messaging within the RCareWorld environment.

What it Implements:
- Initializes the environment with a custom attribute asset.
- Sends and processes a custom message using a custom attribute.
- Sets up a callback function to handle dynamic object messages and demonstrates sending messages with various data types.

What the Functionality Covers:
- Using custom attributes and handling custom messages in RCareWorld.
- Understanding dynamic messaging with support for different data types.

Required Operations:
- Callback Handling: Listens and responds to dynamic object messages.
- Waiting: Simulation steps are used to process the messages.
""")


import os
import sys
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with a custom asset
env = RCareWorld(assets=["CustomAttr"], executable_file=player_path)

# Create an instance of a custom attribute and send a custom message
custom = env.InstanceObject(name="CustomAttr", id=123456, attr_type=attr.CustomAttr)
custom.CustomMessage(message="this is instance channel custom message")

# Perform a simulation step to process the custom message
env.step()

# Print the custom message data
print(custom.data["custom_message"])

# Callback function to handle dynamic object messages
def dynamic_object_callback(args):
    for i, arg in enumerate(args):
        print(f"Arg {i}: {arg}")

# Add a listener for dynamic object messages
env.AddListenerObject("DynamicObject", dynamic_object_callback)

# Send a dynamic object message with various data types
env.SendObject(
    "DynamicObject",
    "string:", "this is dynamic object",
    "int:", 123456,
    "bool:", True,
    "float:", 4849.6564,
    "list:", [616445.085, 9489984.0, 65419596.0, 9849849.0],
    "dict:", {"1": 1, "2": 2, "3": 3},
    "tuple:", ("1", 1, 0.562)
)

# Perform a simulation step to process the dynamic object message
env.step()

# Close the environment
env.Pend()
env.close()
