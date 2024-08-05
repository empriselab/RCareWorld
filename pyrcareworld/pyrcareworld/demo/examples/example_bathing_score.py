# import os
# import sys
# import time
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# from pyrcareworld.envs.base_env import RCareWorld
# from pyrcareworld.attributes.bathing_score_attr import BathingScoreAttr

# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# from pyrcareworld.demo import executable_path
# # Initialize the environment with the specified scene file
# player_path = os.path.join(executable_path, "Player/Player.x86_64")

# env = RCareWorld(executable_file=player_path)
# env.step()

# bathing_score = env.InstanceObject(name="BathingScore", attr_type=BathingScoreAttr)


# target_id = 123 
# target_name = "MyTarget"
# robot_id = 456  
# gripper_name = "Gripper"
# detection_radius = 0.1
# detection_time = 5.0
# is_cloth = False  # True if the target is cloth

# bathing_score.set_target_and_robot(target_id, target_name, robot_id, gripper_name, detection_radius, detection_time, is_cloth)
# env.step()

# bathing_score.start_detection()
# env.step()

# time.sleep(detection_time)

# is_grasp_successful = bathing_score.get_detection_result()
# env.step()

# print(f"Is Grasp Successful: {is_grasp_successful}")

# scores = bathing_score.get_scores()
# print(f"Scores: {scores}")

# file_path = "./scores.json"
# bathing_score.save_scores_to_file(file_path)

# bathing_score.load_scores_from_file(file_path)

# env.close()
