from pyrcareworld.envs import RCareWorld

env = RCareWorld(assets=['Cube'])
env.create_object(id = 2333, name = 'Cube', is_in_scene=False)
cube = env.get_object(2333)
cube.load()
print(env.instance_channel.data)
# env.close()
while True:
    env._step()