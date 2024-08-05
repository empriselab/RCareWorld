from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import cv2
import numpy as np

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "Player/Player.x86_64")

# Initialize the environment
env = RCareWorld(executable_file=player_path)

# Create an instance of a Camera object and set its position and rotation
camera = env.InstanceObject(name="Camera", attr_type=attr.CameraAttr)
camera.SetTransform(position=[-0.1, 0.033, 0.014], rotation=[0, 90, 0])

# Create an instance of a target object and set its properties
target = env.InstanceObject(name="Rigidbody_Sphere", attr_type=attr.RigidbodyAttr)
target.SetDrag(2)
target.EnabledMouseDrag(True)
target.SetUseGravity(False)
target.SetTransform(position=[0, 0.05, 0.015], scale=[0.01, 0.01, 0.01])

# Perform a simulation step
env.step()

# Align the camera to the target
env.AlignCamera(camera.id)
env.SendLog("Click End Pend button to start heat map record")
env.Pend()

# Start heat map recording
camera.StartHeatMapRecord([target.id])
env.SendLog("Drag the sphere to generate heat map")
env.SendLog("Click End Pend button to end heat map record")
env.Pend()

# End heat map recording and retrieve the heat map
camera.EndHeatMapRecord()
camera.GetHeatMap()
env.step()

# Process and save the heat map image
print(camera.data)
print(camera.data["heat_map"])
image_np = np.frombuffer(camera.data["heat_map"], dtype=np.uint8)
image_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
print(image_np.shape)

# Save the heat map image
cv2.imwrite("heatmap.png", image_np)

# Close the environment
env.close()
