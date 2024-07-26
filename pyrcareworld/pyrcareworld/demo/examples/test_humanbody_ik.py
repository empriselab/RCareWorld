import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.humanbody_attr import HumanbodyAttr

env = RCareWorld(executable_file ="/home/cathy/Workspace/rcareworld_new/RCareUnity/Build/TestPlayer.x86_64", scene_file="HumanBodyIK.json")
env.step()
print("This example shows how BioIK works on the human body. It does not show the range of motion of the careavatar with c6-c7 spinal cord injury.")
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

env.Pend()
env.close()
