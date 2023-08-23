import random
import os
from pyrcareworld.envs.base_env import RCareWorldBaseEnv

env = RCareWorldBaseEnv()
env._step()

id = 639787

env.asset_channel.set_action(
    "LoadMesh",
    id=id,
    path=os.path.abspath("../Mesh/002_master_chef_can/google_16k/textured.obj"),
)
env.instance_channel.set_action(
    "SetTransform",
    id=id,
    position=[0, 1, 0],
    rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
)
for _ in range(20):
    env._step()

for i in range(100):
    env.instance_channel.set_action(
        "Copy",
        id=id,
        copy_id=id + i + 1,
    )
    env.instance_channel.set_action(
        "SetTransform",
        id=id + i + 1,
        position=[0, 1, 0],
        rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
    )
    for _ in range(20):
        env._step()

while 1:
    env._step()
