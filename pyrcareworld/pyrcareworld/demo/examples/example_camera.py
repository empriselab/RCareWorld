print("""
This script demonstrates capturing various types of images and bounding boxes using a camera within the RCareWorld environment.

What it Implements:
- Initializes the environment with a camera and a box object.
- Captures and saves multiple image types: RGB, normal map, depth image, amodal mask, and ID map.
- Annotates the ID map with a 2D bounding box and prints both 2D and 3D bounding box information.

What the Functionality Covers:
- Using the RCareWorld camera to capture different image representations.
- Understanding and processing 2D and 3D bounding boxes in the environment.

Required Operations:
- Loop: Processes and prints bounding box information.
- Save Images: Captures and saves images for each frame.
""")

import os
import sys
import cv2
import numpy as np
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

env = RCareWorld(assets=["Camera", "GameObject_Box"], executable_file=player_path)

# Create and set up the camera object
camera = env.InstanceObject(name="Camera", id=123456, attr_type=attr.CameraAttr)
camera.SetTransform(position=[0, 0.25, 0], rotation=[30, 0, 0])

# Create and set up the box object
box = env.InstanceObject(name="GameObject_Box", id=655797, attr_type=attr.GameObjectAttr)
box.SetTransform(position=[0, 0.05, 0.5], scale=[0.1, 0.1, 0.1])
box.SetColor([1, 0, 0, 1])

# Capture and save RGB image
camera.GetRGB(512, 512)
env.step()
rgb = np.frombuffer(camera.data["rgb"], dtype=np.uint8)
rgb = cv2.imdecode(rgb, cv2.IMREAD_COLOR)
cv2.imwrite("rgb.png", rgb)

# Capture and save normal map image
camera.GetNormal(512, 512)
env.step()
normal = np.frombuffer(camera.data["normal"], dtype=np.uint8)
normal = cv2.imdecode(normal, cv2.IMREAD_COLOR)
cv2.imwrite("normal.png", normal)

# Capture and save depth image
camera.GetDepth(0.1, 2.0, 512, 512)
env.step()
depth = np.frombuffer(camera.data["depth"], dtype=np.uint8)
depth = cv2.imdecode(depth, cv2.IMREAD_COLOR)
cv2.imwrite("depth.png", depth)

# Capture and save amodal mask image
camera.GetAmodalMask(655797, 512, 512)
env.step()
amodal_mask = np.frombuffer(camera.data["amodal_mask"], dtype=np.uint8)
amodal_mask = cv2.imdecode(amodal_mask, cv2.IMREAD_COLOR)
cv2.imwrite("amodal_mask.png", amodal_mask)

# Capture and save ID map image
camera.GetID(512, 512)
env.step()
id_map = np.frombuffer(camera.data["id_map"], dtype=np.uint8)
id_map = cv2.imdecode(id_map, cv2.IMREAD_COLOR)
cv2.imwrite("id_map.png", id_map)

# Capture and annotate 2D bounding box
camera.Get2DBBox(512, 512)
env.step()
print("2d_bounding_box:")
print(camera.data)
for i in camera.data["2d_bounding_box"]:
    print(i)
    print(camera.data["2d_bounding_box"][i])
    center = camera.data["2d_bounding_box"][i][0:2]
    size = camera.data["2d_bounding_box"][i][2:4]
    tl_point = (int(center[0] + size[0] / 2), int(512 - center[1] + size[1] / 2))
    br_point = (int(center[0] - size[0] / 2), int(512 - center[1] - size[1] / 2))
    cv2.rectangle(id_map, tl_point, br_point, (255, 255, 255), 1)
cv2.imwrite("id_map_annotated.png", id_map)

# Capture and print 3D bounding box information
camera.Get3DBBox()
env.step()
print("3d_bounding_box:")
for i in camera.data["3d_bounding_box"]:
    print(i)
    print(camera.data["3d_bounding_box"][i])

# Close the environment
env.Pend()
env.close()
