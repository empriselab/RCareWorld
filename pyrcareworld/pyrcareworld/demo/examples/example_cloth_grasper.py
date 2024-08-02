import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.cloth_grasper_attr import ClothGrasper

env = RCareWorld()
env.step()

grasper = env.InstanceObject(name="ClothGrasper", attr_type=ClothGrasper)

cloth_id = 123  
cloth_name = "MyCloth"
robot_id = 456  
gripper_name = "Gripper"
grasp_radius = 0.04

grasper.set_cloth_and_robot(cloth_id, cloth_name, robot_id, gripper_name, grasp_radius)
env.step()


grasper.toggle_grasp_and_gripper()
env.step()

is_held = grasper.is_garment_being_held()
env.step()

print(f"Is Garment Being Held: {is_held}")

env.close()
