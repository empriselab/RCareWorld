print("""
This script demonstrates grasp pose simulation for an object using the GraspSim feature within the RCareWorld environment, and it saves the grasp data to a CSV file.

What it Implements:
- Loads a 3D object mesh and samples points and normals for grasp pose generation.
- Initializes the environment with the GraspSim object and starts the grasp simulation.
- Retrieves the generated grasp poses, including position, orientation (quaternions), and gripper width, then saves this data to a CSV file.

What the Functionality Covers:
- Understanding how to perform grasp pose simulations using the RCareWorld GraspSim feature.
- Integrating point sampling from 3D meshes and saving simulation results to external files.

Required Operations:
- Data Processing: Samples points and normals from a mesh, then processes the grasp simulation results.
- Loop: Continuously steps through the simulation until it is complete.
- Data Saving: Saves the resulting grasp data to a CSV file.
""")


import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.attributes.graspsim_attr import GraspSimAttr
from pyrcareworld.envs.base_env import RCareWorld


try:
    import pandas as pd
except ImportError:
    raise Exception(
        "This feature requires pandas, please install with `pip install pandas`"
    )
try:
    import open3d as o3d
except ImportError:
    raise Exception(
        "This feature requires open3d, please install with `pip install open3d`"
    )
from pyrcareworld.demo import mesh_path
from pyrcareworld.demo import executable_path



def get_grasp_pose(file: str, points_count, scale: float = 1):
    mesh = o3d.io.read_triangle_mesh(file)
    mesh.scale(scale, np.array([0, 0, 0]))
    sample_points = mesh.sample_points_poisson_disk(
        points_count, use_triangle_normal=True
    )
    sample_points.transform([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    points = np.asarray(sample_points.points)
    normals = np.asarray(sample_points.normals)
    return points, normals


obj_path = os.path.join(mesh_path,"drink1/drink1.obj")

points, normals = get_grasp_pose(obj_path, 100)
points = points.reshape(-1).tolist()
normals = normals.reshape(-1).tolist()

executable_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

env = RCareWorld(assets=["GraspSim"], executable_file=executable_path)
grasp_sim = env.InstanceObject(id=123123, name="GraspSim", attr_type=GraspSimAttr)
grasp_sim.StartGraspSim(
    mesh=os.path.abspath(obj_path),
    gripper="franka_hand",
    points=points,
    normals=normals,
    depth_range_min=-0.05,
    depth_range_max=0,
    depth_lerp_count=5,
    angle_lerp_count=5,
    parallel_count=100,
)

# ONLY show grasp pose
# grasp_sim.GenerateGraspPose(mesh=os.path.abspath(obj_path),
#                             gripper='SimpleFrankaGripper',
#                             points=points,
#                             normals=normals,
#                             depth_range_min=-0.05,
#                             depth_range_max=0,
#                             depth_lerp_count=5,
#                             angle_lerp_count=5,
#                             )

env.step()
while not grasp_sim.data['done']:
    env.step()

points = grasp_sim.data["points"]
points = np.array(points).reshape([-1, 3])
quaternions = grasp_sim.data["quaternions"]
quaternions = np.array(quaternions).reshape([-1, 4])
width = grasp_sim.data["width"]
width = np.array(width).reshape([-1, 1])

env.close()

data = np.concatenate((points, quaternions, width), axis=1)
csv = pd.DataFrame(data, columns=["x", "y", "z", "qx", "qy", "qz", "qw", "width"])

csv_path = os.path.join(os.path.dirname(obj_path), "grasps_rfu.csv")
csv.to_csv(csv_path, index=True, header=True)

env.Pend()
env.Pend()
env.close()
