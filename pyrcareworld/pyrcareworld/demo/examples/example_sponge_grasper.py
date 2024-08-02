import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.sponge_grasper_atter import SpongeGrasper

# 初始化环境
env = RCareWorld()
env.step()

grasper = env.InstanceObject(name="SpongeGrasper", attr_type=SpongeGrasper)


sponge_id = 123  
sponge_name = "MySponge"
robot_id = 456  
gripper_name = "Gripper"
grasp_radius = 0.1

grasper.set_sponge_and_robot(sponge_id, sponge_name, robot_id, gripper_name, grasp_radius)
env.step()

grasper.toggle_grasp()
env.step()

is_held = grasper.is_sponge_being_held()
env.step()

print(f"Is Sponge Being Held: {is_held}")

env.close()
