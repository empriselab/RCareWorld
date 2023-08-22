from pyrcareworld.envs import RCareWorld

env = RCareWorld()
for i in range(1000000):
    env._step()
    exit()
