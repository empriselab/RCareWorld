print("""
This script demonstrates the creation of a heat map in the RCareWorld environment by recording interactions with a target object.

What it Implements:
- Initializes the environment with a camera and a target object (a sphere).
- Configures the target object for interaction, including drag and gravity settings.
- Aligns the camera to the target, starts heat map recording during user interaction, and processes the recorded heat map.

What the Functionality Covers:
- Understanding how to set up and use heat map recording in the RCareWorld environment.
- Capturing user interaction data and visualizing it as a heat map.

Required Operations:
- User Interaction: The script requires the user to drag the sphere to generate heat map data.
- Data Processing: Retrieves and processes the heat map image from the recorded data.
- Data Saving: Saves the processed heat map image to a file.
""")


import pyrcareworld.attributes as attr
import cv2
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld


# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

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
# Print the data to check the structure
# print(camera.data)
# print(camera.data["heat_map"])
print("Stop ptinting camera.data for debugging")

heat_map = camera.data.get("heat_map", None)
if heat_map:
    print(heat_map)
    image_np = np.frombuffer(camera.data["heat_map"], dtype=np.uint8)
    image_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    print(image_np.shape)
    cv2.imwrite("heatmap.png", image_np)

else:
    print("Heat map data not found. Skipping this step.")

# Close the environment
env.close()
