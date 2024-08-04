import os
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# Initialize the environment with the specified scene file
env = RCareWorld(scene_file="SimpleYCBModel.json", executable_file="C:\\Users\\15156\\Desktop\\New folder (2)\\Rcareworld.exe")

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
