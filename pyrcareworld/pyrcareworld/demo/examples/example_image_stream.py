print("""
This script demonstrates real-time image capture and display using a camera in the RCareWorld environment while rotating a 3D box object.

What it Implements:
- Initializes the environment with a camera and a box object.
- Captures RGB images from the camera as the box rotates and displays the images in real-time using a separate thread.

What the Functionality Covers:
- Understanding how to capture and process real-time images in RCareWorld.
- Demonstrates multithreading for simultaneous image capture and display.

Required Operations:
- Loop: Continuously captures images and rotates the box object.
- Threading: Uses a separate thread to display images in real-time.
- User Interaction: Allows the user to exit the program by pressing the 'Esc' key or sending a keyboard interrupt (Ctrl+C).
""")


import os
import sys
import cv2
import threading
import numpy as np
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Global variable to store the image
img = None
# Global flag to control the thread
stop_thread = False

# Thread class for displaying images
class ImageThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not stop_thread:
            global img
            if img is not None:
                cv2.imshow("image", img)
                if cv2.waitKey(10) == 27:  # Press 'Esc' to close the window
                    # Setting stop_thread to True to stop the thread
                    global stop_thread
                    stop_thread = True


# Initialize the environment with specified assets
env = RCareWorld(assets=["Camera", "GameObject_Box"], executable_file=player_path)

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
try:
    while True:
        camera.GetRGB(width=512, height=512)
        box.Rotate([0, 1, 0], False)
        env.step()
        image = np.frombuffer(camera.data["rgb"], dtype=np.uint8)
        img = cv2.imdecode(image, cv2.IMREAD_COLOR)
except KeyboardInterrupt:
    print("Exiting the program...")

# In the main thread, after the loop ends, ensure OpenCV windows are properly closed
finally:
    # Stop the thread
    stop_thread = True
    thread.join()
    print("Thread terminated.")
    cv2.destroyAllWindows()  # Ensure this is called in the main thread
