import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.dressing_score_attr import DressingScoreAttr


env = RCareWorld()
env.step()


dressing_score = env.InstanceObject(name="DressingScore", attr_type=DressingScoreAttr)


target_id = 123  
target_name = "MyTarget"
robot_id = 456  
gripper_name = "Gripper"
detection_radius = 0.1
detection_time = 5.0
is_cloth = True  # True if the target is cloth

dressing_score.set_target_and_robot(target_id, target_name, robot_id, gripper_name, detection_radius, detection_time, is_cloth)
env.step()

dressing_score.start_detection()
env.step()

time.sleep(detection_time)

is_grasp_successful = dressing_score.get_detection_result()
env.step()

print(f"Is Grasp Successful: {is_grasp_successful}")

scores = dressing_score.get_scores()
print(f"Scores: {scores}")

file_path = "./dressing_scores.json"
dressing_score.save_scores_to_file(file_path)

dressing_score.load_scores_from_file(file_path)

env.close()
