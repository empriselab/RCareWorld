import os
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

def test_save_model():
    """Tests saving a mesh."""
    env = RCareWorld(scene_file="SimpleYCBModel.json", graphics=False)

    model = []

    for i in env.attrs:
        if type(env.attrs[i]) is attr.RigidbodyAttr:
            model.append(i)

    env.ExportOBJ(model, os.path.abspath("./scene_mesh.obj"))

    env.close()
