from pyrcareworld.envs import RCareWorld

env = RCareWorld()
franka = env.create_robot(
    id=965874, gripper_list=["9658740"], robot_name="franka-panda", base_pos=[0, 0, 0]
)

# target = env.create_object(id=197454, name="Cube", is_in_scene=True)
# position = target.getPosition()
# print(position)
# franka.directlyMoveTo(position)
# for i in range(20):
#     env._step()
while True:
    # position = target.getPosition()
    # print(position)
    # franka.directlyMoveTo(position)
    j = franka.getJointPositions()
    print(j)
    # for i in range(20):
    # env._step()
    franka.setJointPositionsDirectly(j)
    env._step()
