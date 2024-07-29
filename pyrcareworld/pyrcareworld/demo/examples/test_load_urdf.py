from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.utils.rfuniverse_utility as utility
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from demo import urdf_path

def test_load_urdf():
    """Tests loading various URDFs."""
    env = RCareWorld(graphics=False)

    ur5 = env.LoadURDF(path=os.path.join(urdf_path, "UR5/ur5_robot.urdf"), native_ik=True)
    ur5.SetTransform(position=[1, 0, 0])
    yumi = env.LoadURDF(path=os.path.join(urdf_path, "yumi_description/urdf/yumi.urdf"), native_ik=False)
    yumi.SetTransform(position=[2, 0, 0])
    kinova = env.LoadURDF(path=os.path.join(urdf_path, "kinova_gen3/GEN3_URDF_V12.urdf"), native_ik=False)
    kinova.SetTransform(position=[3, 0, 0])
    env.step()

    ur5.IKTargetDoMove(position=[0, 0.5, 0], duration=0.1, relative=True)
    ur5.WaitDo()
    ur5.IKTargetDoMove(position=[0, 0, -0.5], duration=0.1, relative=True)
    ur5.WaitDo()
    ur5.IKTargetDoMove(position=[0, -0.2, 0.3], duration=0.1, relative=True)
    ur5.IKTargetDoRotateQuaternion(
        quaternion=utility.UnityEularToQuaternion([0, 90, 0]), duration=30, relative=True
    )
    ur5.WaitDo()
