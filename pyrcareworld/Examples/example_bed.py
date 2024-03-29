from pyrcareworld.envs import RCareWorld

# from pyrcareworld.envs import DressingEnv
import numpy as np
import pybullet as p
import math

env = RCareWorld()
bed = env.create_bed(
    id=234567,
    name="BedActuation",
    is_in_scene=True,
)

bed.setActuationAngle(10,20)
while True:
    env._step()
