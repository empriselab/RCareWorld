print("""
This script demonstrates loading a 3D mesh and creating multiple copies with random rotations in the RCareWorld environment.

What it Implements:
- Initializes the environment and loads a specified 3D mesh.
- Sets a random initial rotation for the mesh.
- Creates multiple copies of the mesh, each with a different random rotation.

What the Functionality Covers:
- Understanding how to load and manipulate 3D meshes in the RCareWorld environment.
- Demonstrates the creation of multiple mesh instances with varied transformations.

Required Operations:
- Loop: Continuously creates and transforms copies of the mesh.
- Randomization: Applies random rotations to each mesh instance.
""")


import random
import os
import sys

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.demo import mesh_path
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment
env = RCareWorld(executable_file=player_path)
env.step()

# Load a mesh from the specified path
mesh = env.LoadMesh(
    path=os.path.join(mesh_path, "002_master_chef_can/google_16k/textured.obj", )
)

# Set the initial transform of the mesh with random rotation
mesh.SetTransform(
    position=[0, 1, 0],
    rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
)

# Create and transform copies of the mesh
# Change the number of copies as needed. Here, we create 10 copies. Notice the copmputer memory usage.
for i in range(10):
    env.step(20)
    new_mesh = mesh.Copy(new_id=mesh.id + i + 1)
    new_mesh.SetTransform(
        position=[0, 1, 0],
        rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
    )

# End the environment session
env.Pend()
