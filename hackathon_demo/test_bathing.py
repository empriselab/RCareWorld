from pyrcareworld.envs import RCareWorld
import random

env = RCareWorld()
robot = env.create_robot(
    id=12345, gripper_list=["123450"], robot_name="stretch3", base_pos=[0, 0, 0]
)
target = env.create_object(id=2333, name="Cube", is_in_scene=True)
for i in range(10):
    env.step()
while True:
    position = target.getPosition()
    rotation = target.getRotation()
    robot.directlyMoveTo(position)
    env.step()