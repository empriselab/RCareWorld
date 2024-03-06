from pyrcareworld.envs.rcareworld_env import RCareWorldBaseEnv
import cv2
import numpy as np
import os.path as osp
import tempfile
import os
import time


env = RCareWorldBaseEnv()

# env.asset_channel.set_action("InstanceObject", name="Camera", id=123456)
# env.instance_channel.set_action(
#     "SetTransform",
#     id=123456,
#     position=[0, 0.25, 0],
#     rotation=[30, 0, 0],
# )
# env.instance_channel.set_action(
#     "GetDepth", id=123456, width=512, height=512, zero_dis=1, one_dis=5
# )
# env.instance_channel.set_action(
#     "GetDepthEXR",
#     id=123456,
#     width=512,
#     height=512,
# )
# env.instance_channel.set_action("GetRGB", id=123456, width=512, height=512)
# env._step()
# print(env.instance_channel.data[123456]["rgb"])
# # print(env.instance_channel.data[123456]["depth"])
# # print(env.instance_channel.data[123456]["depth_exr"])
# # file = open('/home/cathy/img.png', 'wb')
# # file.write(env.instance_channel.data[123456]['depth'])
# # file.close()
env.instance_channel.set_action(
    "GetDepthEXR",
    id=123456,
    width=512,
    height=1024,
)
env.instance_channel.set_action("GetRGB", id=123456, width=512, height=1024)
env._step()

data_buffer = []


num_animation_seconds = 5
num_frames = num_animation_seconds * 30 + 10

for i in range(num_frames):
    print(f"==> frame {i}")
    env.instance_channel.set_action(
        "GetDepthEXR",
        id=123456,
        width=512,
        height=1024,
    )
    env.instance_channel.set_action("GetRGB", id=123456, width=512, height=1024)
    info = env.instance_channel.data[123456]
    position = info["position"]
    quaternion = info["quaternion"]
    env._step()

    depth_bytes = env.instance_channel.data[123456]["depth_exr"]
    # # temp_file_path = osp.join(tempfile.gettempdir(), "temp_img.exr")
    # # with open(temp_file_path, "wb") as f:
    # #     f.write(depth_bytes)
    # # depth_exr = cv2.imread(temp_file_path, cv2.IMREAD_UNCHANGED)
    # # os.remove(temp_file_path)

    depth_exr = cv2.imdecode(
        np.frombuffer(depth_bytes, dtype=np.uint8), cv2.IMREAD_UNCHANGED
    )

    # mask = np.asarray(o3d.io.read_image(osp.join(mask_path, video_name, view_name, base_name + '.png')))[:, :, 0]
    # foregound_mask = mask == 11
    # depth_png = (depth_exr).astype(np.float32)[:, :]
    # print(np.unique(depth_png))
    # cv2.imwrite(f"data/depth_{i}.jpg", depth_png)

    image_byte = env.instance_channel.data[123456]["rgb"]
    image_rgb = np.frombuffer(image_byte, dtype=np.uint8)
    image_rgb = cv2.imdecode(image_rgb, cv2.IMREAD_COLOR)
    # cv2.imwrite(f"data/rgb_{i}.jpg", image_rgb)

    data_buffer.append((image_rgb, depth_exr, position, quaternion))


for i in range(num_frames):
    image_rgb, depth_png, position, quaternion = data_buffer[i]
    cv2.imwrite(f"data/rgb_{i}.png", image_rgb)
    cv2.imwrite(f"data/depth_{i}.png", depth_png)

    with open(f"data/pose_{i}.txt", "w") as f:
        f.write(
            f"{position[0]} {position[1]} {position[2]} {quaternion[0]} {quaternion[1]} {quaternion[2]} {quaternion[3]}"
        )
