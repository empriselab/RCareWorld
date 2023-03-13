import os
from pyrcareworld.envs import RCareWorld

env = RCareWorld(executable_file='@Editor', assets=['HumanArticulation'])
env.create_human(id=123456, name='HumanArticulation', is_in_scene=False)
human = env.get_human(123456)
human.load()
human.setBasePosition([0, 2, 0])
human.getJointStateByName('Spine1')
env._step()
human.setJointPoisitionByNameDirectly('Neck', [20,20,20])
human.setJointPoisitionByNameDirectly('Spine2', [20,0,0])
env._step()
human.getJointStateByName('Spine1')
while 100:
    env._step()