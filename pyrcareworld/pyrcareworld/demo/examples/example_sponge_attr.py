import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# Initialize the environment with the specified scene file

# Initialize the environment with a custom asset
env = RCareWorld()
print("env initialized")

# Create an instance of a custom attribute and send a custom message
sponge = env.GetAttr(345789)
print("sponge initialized")
# Perform a simulation step to process the custom message
env.step()

# Print the forces data
print(sponge.GetRealTimeForces["forces"])

# Perform another simulation step to ensure continuous updates
env.step()

# Print the forces data again to see the updates
print(sponge.GetRealTimeForces())

# Close the environment
env.Pend()
env.close()
