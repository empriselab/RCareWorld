import pickle
import json

# Load the pickle file
with open("/home/cathy/Downloads/18-0-7.pkl", "rb") as f:
    data = pickle.load(f)

# Convert the data to the desired JSON structure (This depends on your pickle structure)
# For this example, I'm assuming your pickle file has a similar structure as mentioned in the earlier JSON example.

data = data[0]
# json_data = []
print(data[100]["caregiver_info"])

# for frame_data in data:
#     frame_entry = {"frame": frame_data["frame"], "bones": []}

#     for bone_data in frame_data["bones"]:
#         bone_entry = {
#             "startPoint": bone_data["startPoint"],
#             "endPoint": bone_data["endPoint"],
#             "startName": bone_data["startName"],
#             "endName": bone_data["endName"],
#         }
#         frame_entry["bones"].append(bone_entry)

#     json_data.append(frame_entry)

# # Save the data as JSON
# with open("output_data.json", "w") as json_file:
#     json.dump(json_data, json_file)
