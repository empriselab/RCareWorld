from pyrcareworld.envs.rcareworld_env import RCareWorld

# Script to test cloth grasping. Paired with "Cloth Grasp" scene.
if __name__ == "__main__":
    env = RCareWorld()

    # Create a new cloth representation.
    cloth = env.create_cloth(id=100, name="Cloth", is_in_scene=True)

    # Create a new robot.
    robot = env.create_robot(
        id=315893,
        # Note: "3158930" is the scene gripper id, but it seems to not work.
        gripper_list=[315893],
        robot_name="kinova_gen3_7dof-robotiq85",
        base_pos=[0, 0, 0],
    )

    # Note: We use a General Gripper Script on the robot to get the GripperClose() and GripperOpen() functions to have visual effect.

    # ...
    for i in range(200):
        env.step()

    # Move to pants.
    for i in range(100):
        robot.moveTo([0, 0.33, 0.477])
        env.step()

    # Grasp. Cloth Grasper script on C# causes grasp.
    robot.GripperClose()

    # Grasp...
    for i in range(100):
        env.step()

    # Move up.
    for i in range(100):
        robot.moveTo([0, 0.9, 0.3])
        env.step()

    # ...
    for i in range(100):
        env.step()

    # Release.
    robot.GripperOpen()

    # ...
    for i in range(200):
        env.step()
