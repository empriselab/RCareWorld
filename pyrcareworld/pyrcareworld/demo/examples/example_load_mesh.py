import random
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from demo import mesh_path

env = RCareWorld()
env.step()
mesh = env.LoadMesh(
    path=os.path.join("/home/cathy/Workspace/rcareworld_new/pyrcareworld/test/pyrcareworld_test/mesh/", "002_master_chef_can/google_16k/textured.obj")
)
mesh.SetTransform(
    position=[0, 1, 0],
    rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
)

for i in range(100):
    env.step(20)
    new_mesh = mesh.Copy(new_id=mesh.id + i + 1)
    new_mesh.SetTransform(
        position=[0, 1, 0],
        rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
    )
env.Pend()
