import random
import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.demo import mesh_path

# Initialize the environment
env = RCareWorld()
env.step()

# Load a mesh from the specified path
mesh = env.LoadMesh(
    path=os.path.join(mesh_path, "002_master_chef_can/google_16k/textured.obj")
)

# Set the initial transform of the mesh with random rotation
mesh.SetTransform(
    position=[0, 1, 0],
    rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
)

# Create and transform copies of the mesh
for i in range(100):
    env.step(20)
    new_mesh = mesh.Copy(new_id=mesh.id + i + 1)
    new_mesh.SetTransform(
        position=[0, 1, 0],
        rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
    )

# End the environment session
env.Pend()
