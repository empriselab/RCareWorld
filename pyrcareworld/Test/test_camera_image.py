from pyrcareworld.envs.base_env import RCareWorldBaseEnv
import cv2
import numpy as np

env = RCareWorldBaseEnv()

env.asset_channel.set_action("InstanceObject", name="Camera", id=123456)
env.instance_channel.set_action(
    "SetTransform",
    id=123456,
    position=[0, 0.25, 0],
    rotation=[30, 0, 0],
)
env.instance_channel.set_action(
    "GetDepth", id=123456, width=512, height=512, zero_dis=1, one_dis=5
)
env.instance_channel.set_action(
    "GetDepthEXR",
    id=123456,
    width=512,
    height=512,
)
env.instance_channel.set_action("GetRGB", id=123456, width=512, height=512)
env._step()
print(env.instance_channel.data[123456]["rgb"])
print(env.instance_channel.data[123456]["depth"])
print(env.instance_channel.data[123456]["depth_exr"])
# file = open('/home/yanbing/img.png', 'wb')
# file.write(env.instance_channel.data[123456]['rgb'])
# file.close()
image_np = np.frombuffer(env.instance_channel.data[123456]["rgb"], dtype=np.uint8)
image_nd = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
print(image_nd.shape)
cv2.imshow("dst", image_nd)
cv2.waitKey(0)
env.close()

# while 1:
#     env._step()
