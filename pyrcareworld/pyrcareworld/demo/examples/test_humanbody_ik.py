import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.humanbody_attr import HumanbodyAttr

def test_humanbody_ik():
    """Test BioIK for human body inverse kinematics.
    
    Note that this test does not show the range of motion of the careavatar
    with c6-c7 spinal cord injury.
    """
    env = RCareWorld(scene_file="HumanBodyIK.json", graphics=False)
    env.step()
    human = env.GetAttr(168242)
    for index in range(5):
        human.HumanIKTargetDoMove(
            index=index, position=[0, 0, 0.5], duration=1, speed_based=False, relative=True
        )
        human.WaitDo()
        human.HumanIKTargetDoMove(
            index=index, position=[0, 0.5, 0], duration=1, speed_based=False, relative=True
        )
        human.WaitDo()
        human.HumanIKTargetDoMove(
            index=index, position=[0, 0, -0.5], duration=1, speed_based=False, relative=True
        )
        human.WaitDo()
        human.HumanIKTargetDoMove(
            index=index, position=[0, -0.5, 0], duration=1, speed_based=False, relative=True
        )
        human.WaitDo()

    env.close()
