import os
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

env = RCareWorld(scene_file="SimpleYCBModel.json")

model = []

for i in env.attrs:
    if type(env.attrs[i]) is attr.RigidbodyAttr:
        model.append(i)

env.ExportOBJ(model, os.path.abspath("./scene_mesh.obj"))

env.Pend()
env.close()
