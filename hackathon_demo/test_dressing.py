from pyrcareworld.envs.rcareworld_env import RCareWorld
import numpy as np

def move_slowly(robot, start_pos, end_pos, steps):
    """Move the robot slowly from start_pos to end_pos in a given number of steps."""
    start_pos = np.array(start_pos)
    end_pos = np.array(end_pos)
    for i in range(steps):
        alpha = i / steps
        current_target = start_pos * (1 - alpha) + end_pos * alpha
        robot.directlyMoveTo(list(current_target))
        env.step()
        
    print("Done moving through" + str(end_pos))
            


if __name__ == "__main__":
    env = RCareWorld()
    cloth = env.create_cloth(id=100, name="Gown", is_in_scene=True)
    
    robot = env.create_robot(
        id=315893, 
        gripper_list=[315893], 
        robot_name="kinova_gen3_7dof-robotiq85", 
        base_pos=[-0.231, 0, 0],    
    )

    cube = env.create_object(id=11234, name="Cube1", is_in_scene=True)
   
    
    """
    Initial Point Config
    """
    initial_position = [0.02, 0.6, 0.4]
    
    left_sleeve = [-0.1, 0.3, 0.5]
    left_arm = [0.2, 0.6, -0.3]

    
    print('\n' + "-----start moving to left sleeve------" + '\n')
    # move_slowly(robot, initial_position, left_sleeve, 100)\
    move_slowly(robot, initial_position, left_sleeve, 300)
    robot.GripperClose()