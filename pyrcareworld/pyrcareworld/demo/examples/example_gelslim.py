print("""
This script demonstrates the use of a GelSlim sensor within the RCareWorld environment to capture and manipulate light and depth images.

What it Implements:
- Initializes the environment with a GelSlim sensor and a target object.
- Applies forces to the target object and captures the resulting light and depth images from the GelSlim sensor.
- Applies a blur effect to the GelSlim sensor and captures the updated images.

What the Functionality Covers:
- Understanding how to instantiate and position GelSlim sensors and target objects in RCareWorld.
- Learning how to apply forces to objects and retrieve sensor data such as light and depth images.
- Demonstrates image manipulation techniques by applying blur to the sensor data.

Required Operations:
- Loop: Applies force to the target object over multiple simulation steps.
- Image Capture: Retrieves and saves sensor data at different stages of the simulation.
""")


import os
import sys
import cv2
import numpy as np

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
from pyrcareworld.attributes.gelslim_attr import GelSlimAttr
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment
env = RCareWorld(executable_file=player_path)

# Create an instance of a GelSlim object and set its position
gelslim = env.InstanceObject(name="GelSlim", attr_type=GelSlimAttr)
gelslim.SetTransform(position=[0, 0, 0])

# Create an instance of a target object and set its position and rotation
target = env.InstanceObject(name="GelSlimTarget", attr_type=attr.RigidbodyAttr)
target.SetTransform(position=[0, 0.03, 0], rotation=[90, 0, 0])

# Set the view transform for the environment
env.SetViewTransform(position=[-0.1, 0.03, 0], rotation=[0, 90, 0])

# Apply force to the target object for 50 steps
for i in range(50):
    env.step()
    target.AddForce([0, -1, 0])

# Retrieve and save light image data
gelslim.GetData()
env.step()
light_image = np.frombuffer(gelslim.data["light"], dtype=np.uint8)
light_image = cv2.imdecode(light_image, cv2.IMREAD_COLOR)
cv2.imwrite("light_image.png", light_image)

# Retrieve and save depth image data
depth_image = np.frombuffer(gelslim.data["depth"], dtype=np.uint8)
depth_image = cv2.imdecode(depth_image, cv2.IMREAD_GRAYSCALE)
cv2.imwrite("depth_image.png", depth_image)

# Apply blur to GelSlim and save updated light and depth images
gelslim.BlurGel()
gelslim.GetData()
env.step()

# Save updated light image
light_image_blurred = np.frombuffer(gelslim.data["light"], dtype=np.uint8)
light_image_blurred = cv2.imdecode(light_image_blurred, cv2.IMREAD_COLOR)
cv2.imwrite("light_image_blurred.png", light_image_blurred)

# Save updated depth image
depth_image_blurred = np.frombuffer(gelslim.data["depth"], dtype=np.uint8)
depth_image_blurred = cv2.imdecode(depth_image_blurred, cv2.IMREAD_GRAYSCALE)
cv2.imwrite("depth_image_blurred.png", depth_image_blurred)

# Close the environment
env.Pend()
env.close()
