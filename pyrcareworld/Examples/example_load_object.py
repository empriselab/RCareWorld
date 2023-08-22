from pyrcareworld.envs import RCareWorld

env = RCareWorld(assets=["Cube"])
cube = env.create_object(id=2333, name="Cube", is_in_scene=False)
cube.load()
print(env.instance_channel.data)
# env.close()
while True:
    env._step()
