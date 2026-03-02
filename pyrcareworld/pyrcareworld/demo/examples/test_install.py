import random
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# Initialize the environment with the specified assets and set the time step
env = RCareWorld(executable_file="@editor")

cube = env.GetAttr(1234)
env.step()

print(cube.data)
