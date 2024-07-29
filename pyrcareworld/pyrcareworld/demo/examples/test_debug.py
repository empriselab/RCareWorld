from pyrcareworld.envs.base_env import RCareWorld

def test_debug():
    """Test various debug commands."""
    env = RCareWorld(scene_file="DebugScene.json", graphics=False)

    env.DebugGraspPoint()
    env.SendLog("DebugGraspPoint")
    env.step(300)
    env.DebugGraspPoint(False)

    env.DebugObjectID()
    env.SendLog("DebugObjectID")
    env.step(300)
    env.DebugObjectID(False)

    env.DebugObjectPose()
    env.SendLog("DebugObjectPose")
    env.step(300)
    env.DebugObjectPose(False)

    env.DebugColliderBound()
    env.SendLog("DebugColliderBound")
    env.step(300)
    env.DebugColliderBound(False)

    env.DebugCollisionPair()
    env.SendLog("DebugCollisionPair")
    env.step(300)
    env.DebugCollisionPair(False)

    env.Debug3DBBox()
    env.SendLog("Debug3DBBox")
    env.step(300)
    env.Debug3DBBox(False)

    env.Debug2DBBox()
    env.SendLog("Debug2DBBox")
    env.step(300)
    env.Debug2DBBox(False)

    env.DebugJointLink()
    env.SendLog("DebugJointLink")
    env.step(300)
    env.DebugJointLink(False)
