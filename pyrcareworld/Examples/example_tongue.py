from pyrcareworld.envs import RCareWorld

env = RCareWorld(executable_file='/home/cathy/Workspace/rfu_063/Build/Tongue/tongue.x86_64')
while True:
    env._step()