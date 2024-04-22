from pyrcareworld.envs import RCareWorld
import random

# env = RCareWorld(executable_file="/home/cathy/Workspace/RCareUnity/Build/Bathing/Ubuntu/bathing_ubuntu.x86_64")
env = RCareWorld(executable_file="@Editor")
robot = env.create_robot(
    id=123456, gripper_list=[123456], robot_name="stretch3", base_pos=[0, 0, 0]
)
target = env.create_object(id=2333, name="Cube", is_in_scene=True)
for i in range(10):
    env.step()
env.step()

while True:
    position = target.getPosition()
    print(position)
    robot.BioIKMove(position)
    env.step()
