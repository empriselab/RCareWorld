from pyrcareworld.envs import RCareWorld

env = RCareWorld(scene_file='my_new_scene.json')
print(env.instance_channel.data)
while True:
    env._step()
