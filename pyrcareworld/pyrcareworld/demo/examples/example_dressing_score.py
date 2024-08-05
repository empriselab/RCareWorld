# import os
# import sys
# import time
# import json
# # Add the project directory to the system path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# from pyrcareworld.envs.base_env import RCareWorld
# from pyrcareworld.attributes.dressing_score_attr import DressingScoreAttr

# from pyrcareworld.demo import executable_path
# # Initialize the environment with the specified scene file
# player_path = os.path.join(executable_path, "Player/Player.x86_64")

# # Initialize the environment with the specified executable file
# env = RCareWorld(executable_file=player_path)
# env.step()

# # Create an instance of the DressingScore attribute
# dressing_score = env.InstanceObject(name="DressingScore", attr_type=DressingScoreAttr)

# # Perform some actions in the environment (this part is assumed as per your example logic)
# # Here, we simulate the waiting time to collect some scores
# time.sleep(5)

# # Get the detection result (this part is assumed based on your logic)
# is_grasp_successful = dressing_score.get_scores()
# env.step()

# # Print the detection result
# print(f"Is Grasp Successful: {is_grasp_successful}")

# # Get and print the scores
# scores = dressing_score.get_scores()
# print(f"Scores: {scores}")

# # Define the file path to save the scores
# file_path = "./dressing_scores.json"

# # Save the scores to a file
# dressing_score.save_scores_to_file(file_path)

# # Load the scores from the file
# dressing_score.load_scores_from_file(file_path)

# # Verify loaded scores
# loaded_scores = dressing_score.get_scores()
# print(f"Loaded Scores: {loaded_scores}")

# # Close the environment session
# env.close()
