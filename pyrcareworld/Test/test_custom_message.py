from pyrcareworld.envs.base_env import RCareWorldBaseEnv
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)

env = RCareWorldBaseEnv(assets=["CustomAttr"])

# asset_channel custom message
env.asset_channel.set_action(
    "CustomMessage", message="this is a asset channel python to unity custom message"
)
env._step()
msg = env.asset_channel.data["custom_message"]
print(msg)


# instance_channel custom message
env.asset_channel.set_action("InstanceObject", name="CustomAttr", id=123456)
env.instance_channel.set_action(
    "CustomMessage",
    id=123456,
    message="this is a instance channel python to unity custom message",
)
env._step()
msg = env.instance_channel.data[123456]["custom_message"]
print(msg)


# listener message
def listener_test(msg: IncomingMessage):
    print(msg.read_string())
    print(msg.read_int32())
    print(msg.read_float32())
    print(msg.read_bool())
    print(msg.read_float32_list())


env.asset_channel.AddListener("ListenerMessage", listener_test)
env.asset_channel.SendMessage(
    "ListenerMessage",
    123456,
    "this is a python to unity listener message",
    True,
    4849.6564,
    [616445.085, 9489984.0, 65419596.0, 9849849.0],
)
env._step()


while 1:
    env._step()
