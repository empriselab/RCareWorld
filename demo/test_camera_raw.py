from pyrcareworld.envs import RCareWorld
import cv2
import numpy as np

env = RCareWorld(executable_file="@Editor")


env.instance_channel.set_action("GetRGB", id=654321, width=512, height=1024)
info = env.instance_channel.data[654321]

env.step()
image_byte = env.instance_channel.data[654321]["rgb"]
image_rgb = np.frombuffer(image_byte, dtype=np.uint8)
image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
cv2.imshow("show", image_rgb)
cv2.waitKey(0)
