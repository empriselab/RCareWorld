print("""
This script demonstrates the creation and control of a camera and a box object within the RCareWorld environment, capturing RGB images with random box colors.

What it Implements:
- Initializes the environment with camera and box objects.
- Sets random colors for the box and captures RGB images using the camera.
- Saves the captured images and optionally displays them using OpenCV.

What the Functionality Covers:
- Object instantiation and manipulation within the RCareWorld environment.
- Camera positioning and orientation.
- Capturing and processing images.

Required Operations:
- Loop: Continuously sets random colors, captures images, and updates the environment.
- Optional: Viewing the images with OpenCV in real-time.
""")

import random
import cv2
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with specified assets
env = RCareWorld(assets=["Camera", "GameObject_Box"], executable_file=player_path)

# Instantiate a camera object
camera = env.InstanceObject(name="Camera", id=123456, attr_type=attr.CameraAttr)

# Instantiate a box object and set its properties
box = env.InstanceObject(name="GameObject_Box", attr_type=attr.GameObjectAttr)
box.SetTransform(position=[0, 0.05, 0.5], scale=[0.1, 0.1, 0.1])

# Function to generate a random color
def random_color():
    return [random.random(), random.random(), random.random(), 1]

# Set a random color for the box
color = random_color()
box.SetColor(color)

# Perform a simulation step to update the environment
env.step()

# Function to save and read RGB image
def save_and_read_image(camera, filename):
    with open(filename, 'wb') as f:
        f.write(camera.data["rgb"])
    image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    return image

# Main loop to capture images
print("Stop printing image.shape for debugging")

for i in range(600):
    # Set a random color for the box
    color = random_color()
    box.SetColor(color)

    # Perform a simulation step to update the environment
    env.step()
    
    # Set camera position and orientation
    camera.SetTransform(position=[0, 0.25, 0], rotation=[30, 0, 0])
    camera.LookAt(target=box.data["position"])

    # Capture RGB image
    camera.GetRGB(width=512, height=512)
    env.step()

    # Save and read the captured image
    image = save_and_read_image(camera, "image_test.png")

    # Print the shape of the captured image!
    # print(image.shape)

    # Optional: Display the image using OpenCV
    # cv2.imshow("RGB Image", image)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Close the OpenCV window
# cv2.destroyAllWindows()

# Close the environment
env.Pend()
env.close()
