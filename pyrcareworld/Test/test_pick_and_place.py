import random
from pyrcareworld.envs.base_env import RCareWorldBaseEnv

env = RCareWorldBaseEnv()

env.asset_channel.set_action("InstanceObject", name="franka_panda", id=123456)
env.instance_channel.set_action(
    "SetIKTargetOffset",
    id=123456,
    position=[0, 0.105, 0],
)
for i in range(200):
    env.step()

env.instance_channel.set_action(
    "GripperOpen",
    id=1234560,
)
env.instance_channel.set_action(
    "IKTargetDoMove",
    id=123456,
    position=[0, 0.7, 0.5],
    duration=0,
    speed_based=False,
)
env.instance_channel.set_action(
    "IKTargetDoRotate",
    id=123456,
    vector3=[0, 45, 180],
    duration=0,
    speed_based=False,
)
env.step()
while (
    not env.instance_channel.data[123456]["move_done"]
    or not env.instance_channel.data[123456]["rotate_done"]
):
    env.step()

while 1:
    env.asset_channel.set_action("InstanceObject", name="Rigidbody_Box", id=111111)
    env.instance_channel.set_action(
        "SetTransform",
        id=111111,
        position=[random.uniform(-0.5, -0.3), 0.03, random.uniform(0.3, 0.5)],
        scale=[0.06, 0.06, 0.06],
    )
    env.asset_channel.set_action("InstanceObject", name="Rigidbody_Box", id=222222)
    env.instance_channel.set_action(
        "SetTransform",
        id=222222,
        position=[random.uniform(0.3, 0.5), 0.03, random.uniform(0.3, 0.5)],
        scale=[0.06, 0.06, 0.06],
    )
    for i in range(100):
        env.step()

    position1 = env.instance_channel.data[111111]["position"]
    position2 = env.instance_channel.data[222222]["position"]

    env.instance_channel.set_action(
        "IKTargetDoMove",
        id=123456,
        position=[position1[0], position1[1] + 0.5, position1[2]],
        duration=2,
        speed_based=False,
    )
    env.step()
    while not env.instance_channel.data[123456]["move_done"]:
        env.step()
    env.instance_channel.set_action(
        "IKTargetDoMove",
        id=123456,
        position=[position1[0], position1[1], position1[2]],
        duration=2,
        speed_based=False,
    )
    env.step()
    while not env.instance_channel.data[123456]["move_done"]:
        env.step()
    env.instance_channel.set_action(
        "GripperClose",
        id=1234560,
    )
    for i in range(50):
        env.step()
    env.instance_channel.set_action(
        "IKTargetDoMove",
        id=123456,
        position=[0, 0.5, 0],
        duration=2,
        speed_based=False,
        relative=True,
    )
    env.step()
    while not env.instance_channel.data[123456]["move_done"]:
        env.step()
    env.instance_channel.set_action(
        "IKTargetDoMove",
        id=123456,
        position=[position2[0], position2[1] + 0.5, position2[2]],
        duration=4,
        speed_based=False,
    )
    env.step()
    while not env.instance_channel.data[123456]["move_done"]:
        env.step()
    env.instance_channel.set_action(
        "IKTargetDoMove",
        id=123456,
        position=[position2[0], position2[1] + 0.06, position2[2]],
        duration=2,
        speed_based=False,
    )
    env.step()
    while not env.instance_channel.data[123456]["move_done"]:
        env.step()
    env.instance_channel.set_action(
        "GripperOpen",
        id=1234560,
    )
    for i in range(50):
        env.step()
    env.instance_channel.set_action(
        "IKTargetDoMove",
        id=123456,
        position=[0, 0.5, 0],
        duration=2,
        speed_based=False,
        relative=True,
    )
    env.step()
    while not env.instance_channel.data[123456]["move_done"]:
        env.step()
    env.instance_channel.set_action(
        "IKTargetDoMove",
        id=123456,
        position=[0, 0.7, 0.5],
        duration=2,
        speed_based=False,
    )
    env.step()
    while not env.instance_channel.data[123456]["move_done"]:
        env.step()
    env.instance_channel.set_action(
        "Destroy",
        id=111111,
    )
    env.instance_channel.set_action(
        "Destroy",
        id=222222,
    )
    env.step()
