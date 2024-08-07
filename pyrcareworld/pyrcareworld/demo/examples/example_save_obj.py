import os
import pyrcareworld.attributes as attr
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "Player/Player.x86_64")
# Initialize the environment with the specified scene file
env = RCareWorld(scene_file="SimpleYCBModel.json", executable_file=player_path)

# List to store model IDs
model_ids = []

# Iterate through the environment attributes to find RigidbodyAttr objects
for attr_id in env.attrs:
    if isinstance(env.attrs[attr_id], attr.RigidbodyAttr):
        model_ids.append(attr_id)

# Export the models as an OBJ file
output_path = os.path.abspath("./scene_mesh.obj")
env.ExportOBJ(model_ids, output_path)
print(f"Scene mesh exported to {output_path}")

# End the environment session
env.Pend()
env.close()
