# import pyrcareworld.attributes as attr
# from pyrcareworld.envs.base_env import RCareWorld

# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# from pyrcareworld.demo import executable_path
# # Initialize the environment with the specified scene file
# player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# class ClothScore:
#     def __init__(self, asset_name):
#         self.env = RCareWorld(assets=[asset_name], executable_file=player_path)
#         self.cloth_instance = self.env.create_instance(name=asset_name, id=123456, attr_type=attr.CustomAttr)
    
#     def send_custom_message(self, message):
#         self.cloth_instance.CustomMessage(message=message)
#         self.env.step()
#         return self.cloth_instance.data["custom_message"]

#     def calculate_cloth_score(self):
#         msg = self.env.get_message()
#         data_dict = self.parse_message(msg)
#         score = self.score_forces(data_dict)
#         return score

#     def parse_message(self, msg):
#         object_data = attr.base_attr.parse_message(msg)
#         attributes = {
#             "forearm_hole_likelihood": msg.read_float32(),
#             "upperarm_hole_likelihood": msg.read_float32(),
#             "forearm_distance": msg.read_float32(),
#             "upperarm_distance": msg.read_float32(),
#             "shoulder_coverage": msg.read_float32(),
#             "arm_coverage": msg.read_float32()
#         }
#         object_data.update(attributes)
#         return object_data

#     def score_forces(self, data):
#         arm_distance_score = (data["forearm_distance"] + data["upperarm_distance"]) / 2
#         hole_likelihood = max(data["forearm_hole_likelihood"], data["upperarm_hole_likelihood"])
#         coverage_score = data["shoulder_coverage"] + data["arm_coverage"]
#         overall_score = arm_distance_score * hole_likelihood + coverage_score
#         return overall_score

# if __name__ == "__main__":
#     scorer = ClothScore(asset_name="ClotrhScoreAttr")
#     custom_message = scorer.send_custom_message("this is instance cloth score message")
#     print("Received Custom Message:", custom_message)
#     final_score = scorer.calculate_cloth_score()
#     print("Calculated Cloth Score:", final_score)
