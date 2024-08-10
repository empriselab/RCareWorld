print("""
This script demonstrates various debugging tools available in the RCareWorld environment by visualizing different aspects of the scene.

What it Implements:
- Initializes the environment with a specific scene file.
- Activates and deactivates multiple debugging modes, such as grasp points, object IDs, object poses, collider bounds, collision pairs, and bounding boxes.

What the Functionality Covers:
- Understanding the visual debugging tools in RCareWorld for various scene components.
- Learning how to log and step through debugging processes in the environment.

Required Operations:
- Waiting: The script waits for a specified number of steps in each debugging mode before deactivating it.
""")

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with the specified scene file
env = RCareWorld(scene_file="DebugScene.json", executable_file=player_path)


# Debug Grasp Point
env.DebugGraspPoint()
env.SendLog("DebugGraspPoint")
env.step(300)
env.DebugGraspPoint(False)

# Debug Object ID
env.DebugObjectID()
env.SendLog("DebugObjectID")
env.step(300)
env.DebugObjectID(False)

# Debug Object Pose
env.DebugObjectPose()
env.SendLog("DebugObjectPose")
env.step(300)
env.DebugObjectPose(False)

# Debug Collider Bound
env.DebugColliderBound()
env.SendLog("DebugColliderBound")
env.step(300)
env.DebugColliderBound(False)

# Debug Collision Pair
env.DebugCollisionPair()
env.SendLog("DebugCollisionPair")
env.step(300)
env.DebugCollisionPair(False)

# Debug 3D Bounding Box
env.Debug3DBBox()
env.SendLog("Debug3DBBox")
env.step(300)
env.Debug3DBBox(False)

# Debug 2D Bounding Box
env.Debug2DBBox()
env.SendLog("Debug2DBBox")
env.step(300)
env.Debug2DBBox(False)

# Debug Joint Link
env.DebugJointLink()
env.SendLog("DebugJointLink")
env.step(300)
env.DebugJointLink(False)
