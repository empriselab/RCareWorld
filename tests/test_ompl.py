"""Tests for the OMPL"""

import os
import sys
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.omplmanager_attr import OmplManagerAttr

try:
    import pyrcareworld.attributes.omplmanager_attr as rfu_ompl
except ImportError:
    raise Exception("This feature requires ompl, see: https://github.com/ompl/ompl")


from pyrcareworld.demo import executable_path
# Initialize the environment with the specified scene file

def test_ompl():
    player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

    env = RCareWorld(assets=["franka_panda", "Collider_Box", "OmplManager"], executable_file=player_path, graphics=False)
    robot = env.InstanceObject(
        name="franka_panda", id=123456, attr_type=attr.ControllerAttr
    )
    robot.EnabledNativeIK(False)
    box1 = env.InstanceObject(name="Collider_Box", id=111111, attr_type=attr.ColliderAttr)
    box1.SetTransform(position=[-0.5, 0.5, 0], scale=[0.2, 1, 0.2])
    box2 = env.InstanceObject(name="Collider_Box", id=111112, attr_type=attr.ColliderAttr)
    box2.SetTransform(position=[0.5, 0.5, 0], scale=[0.2, 1, 0.2])
    env.step()

    ompl_manager = env.InstanceObject(name="OmplManager", attr_type=attr.OmplManagerAttr)
    ompl_manager.modify_robot(123456)
    env.step()

    start_state = [0.0, -45.0, 0.0, -135.0, 0.0, 90.0, 45.0]
    target_state = [1.0, -45.0, 0.0, -135.0, 0.0, 90.0, 45.0]
    # target_state = [
    #     6.042808,
    #     -35.73029,
    #     -128.298,
    #     -118.3777,
    #     -40.28789,
    #     134.8007,
    #     -139.2552,
    # ]

    planner = rfu_ompl.RFUOMPL(ompl_manager, time_unit=5)

    ompl_manager.set_state(start_state)
    env.step(50)

    ompl_manager.set_state(target_state)
    env.step(50)

    ompl_manager.set_state(start_state)
    env.step(50)

    env.SetTimeStep(0.001)
    env.step()

    is_sol, path = planner.plan_start_goal(start_state, target_state)

    assert path is not None

    # print(target_state)
    # print(path[-1])

    # env.SetTimeStep(0.02)
    # env.step()
    # if is_sol:
    #     planner.execute(path)
    