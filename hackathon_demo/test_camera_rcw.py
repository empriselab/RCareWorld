from pyrcareworld.envs import RCareWorld
import cv2
import numpy as np

env = RCareWorld(executable_file="@Editor")
cam = env.create_camera(id=654321, name="Camera", width=512, height=1024, is_in_scene=True)
image_rgb = cam.getRGB()
image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
cv2.imshow("show", image_rgb)
cv2.waitKey(0)

