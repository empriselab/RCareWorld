import threading
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import cv2
import numpy as np

# Global variable to store the image
img = None

# Thread class for displaying images
class ImageThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            global img
            if img is not None:
                cv2.imshow("image", img)
                cv2.waitKey(10)

# Initialize the environment with specified assets
env = RCareWorld(assets=["Camera", "GameObject_Box"])

# Create and set up the camera object
camera = env.InstanceObject(name="Camera", id=123456, attr_type=attr.CameraAttr)
camera.SetTransform(position=[0, 0.25, 0], rotation=[30, 0, 0])

# Create and set up the box object
box = env.InstanceObject(name="GameObject_Box", attr_type=attr.GameObjectAttr)
box.SetTransform(position=[0, 0.05, 0.5], scale=[0.1, 0.1, 0.1])
box.SetColor([1, 0, 0, 1])

# Start the image display thread
thread = ImageThread()
thread.start()

# Main loop to capture images and rotate the box
while True:
    camera.GetRGB(width=512, height=512)
    box.Rotate([0, 1, 0], False)
    env.step()
    image = np.frombuffer(camera.data["rgb"], dtype=np.uint8)
    img = cv2.imdecode(image, cv2.IMREAD_COLOR)
