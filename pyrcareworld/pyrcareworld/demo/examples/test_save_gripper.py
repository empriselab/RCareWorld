import os
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

def test_save_gripper():
    """Tests exporting a mesh for a known gripper."""
    # supported gripper: allegro_hand_right, bhand, dh_robotics_ag95_gripper, franka_hand, svh
    env = RCareWorld(assets=["allegro_hand_right"], graphics=False)
    bhand = env.InstanceObject("allegro_hand_right", attr_type=attr.ControllerAttr)
    env.step(5)
    moveable_joint_count = bhand.data["number_of_moveable_joints"]
    print(f"moveable_joint_count:{moveable_joint_count}")
    bhand.SetJointPositionDirectly([30 for _ in range(moveable_joint_count)])
    env.step(5)
    env.ExportOBJ([bhand.id], os.path.abspath("./gripper_mesh.obj"))
    env.close()
