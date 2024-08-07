from pyrcareworld.envs.base_env import RCareWorld

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "Player/Player.x86_64")

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
