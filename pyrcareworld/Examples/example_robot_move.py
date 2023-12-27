from pyrcareworld.envs import RCareWorld

env = RCareWorld()
robot = env.create_robot(
    id=315892,
    gripper_list=["3158920"],
    robot_name="kinova_gen3_7dof-robotiq85",
    # base_pos=[7.74100018,14.8170004,10.4515963],
)
target = env.create_object(id=1000, name="Cube", is_in_scene=True)
# robot.load()
while True:
    position = target.getPosition()
    env._step()
    # print(position)
    robot.directlyMoveTo(position)
    print(robot.getRobotState())
    env._step()