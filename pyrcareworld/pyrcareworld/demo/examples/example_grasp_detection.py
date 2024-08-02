import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.grasp_detection_attr import GraspDetectionAttr

env = RCareWorld()
env.step()

grasper = env.InstanceObject(name="GraspDetection", attr_type=GraspDetectionAttr)

target_id = 123  
target_name = "MyTarget"
robot_id = 456  
gripper_name = "Gripper"
detection_radius = 0.1
detection_time = 5.0
is_cloth = False 

grasper.set_target_and_robot(target_id, target_name, robot_id, gripper_name, detection_radius, detection_time, is_cloth)
env.step()

grasper.start_detection()
env.step()


time.sleep(detection_time)

is_grasp_successful = grasper.get_detection_result()
env.step()

print(f"Is Grasp Successful: {is_grasp_successful}")

env.close()
