import json
from pyrcareworld.envs.bathing_env import BathingEnv
import numpy as np
import cv2
import argparse

def _main(use_graphics=False):
    if use_graphics:
        text = """
        An example of the usage of the bathing environment.

        The sponge will be attached to the robot's hand if the grasp center and the sponge are close enough. (distance < 0.1m)  
        The sponge will be detached from the robot's hand if you call the GripperOpen() function.

        You can obtain low level information of the sponge, the robot, and use unlimited numbers of cameras to observe the scene.

        The threshold for a comfortable force on the human body is set to 1-6N.

        Check the website detailed rubric. After each run of the simulation, a json file will be generated in the current directory (~/.config/unity3d/RCareWorld/BathingPlayer).

        The path may be different according to the OS and your computer configuration.
        """

        print(text) 
    # Initialize the environment
    env = BathingEnv(graphics=use_graphics)
    print(env.attrs)

    stretch_id = 221582
    robot = env.GetAttr(stretch_id)
    env.step()

    # Control the gripper
    gripper = env.GetAttr(2215820)
    gripper.GripperOpen()
    env.step(300)

    gripper.GripperClose()
    env.step()

    # Obtain sponge data and simulate a step
    sponge = env.GetAttr(91846)
    env.step()
    print(sponge.data)

    # Camera operations: Attach a camera to the robot's hand
    camera_hand = env.GetAttr(654321)
    camera_hand.SetTransform(position=gripper.data['position'], rotation=[0, 0, 0])
    camera_hand.SetParent(2215820)
    camera_hand.GetRGB(512, 512)
    env.step()
    rgb = np.frombuffer(camera_hand.data["rgb"], dtype=np.uint8)
    rgb = cv2.imdecode(rgb, cv2.IMREAD_COLOR)
    cv2.imwrite("rgb_hand.png", rgb)

    # Move the robot to specified positions
    position1 = (-0.657, 0.941, 1.645)
    position2 = (-0.263, 1.063, 1.645)

    robot.IKTargetDoMove(
        position=[position1[0], position1[1] + 0.5, position1[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position1[0], position1[1], position1[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()
    gripper.GripperClose()
    env.step(50)
    robot.IKTargetDoMove(
        position=[0, 0.5, 0], duration=2, speed_based=False, relative=True
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position2[0], position2[1] + 0.5, position2[2]],
        duration=4,
        speed_based=False,
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position2[0], position2[1] + 0.06, position2[2]],
        duration=2,
        speed_based=False,
    )
    
    """
        The machine's movement speed is related to the time in the step() method, as well as the defined distance and speed.
        
        - If the time is too short, the machine will accelerate, which may cause the robot to break down and fall apart.
        
        - If the time is too long, the machine may experience friction, leading to slow drifting.
        
        - Therefore, when you want to achieve precise movement, make sure to calculate the appropriate time, which is a simple inverse and linear relationship with speed and distance.
        
        - If you notice that the machine isn't moving, it means the speed is too slow; please increase the speed.
        
        - If you observe significant stretching in the arm above the stretch, it indicates that the movement is too fast, which can lead to instability; please reduce the speed to seek stability.
        
        - If the robot jumps, it indicates that the initial speed is too high. Please reduce the speed, or move slightly toward the target direction first, then gradually increase the speed.

        - If you notice that after the robot's movement has ended, the arm is retracting, and the robot is slowly rotating, 
        # this is due to angular momentum and the inertia of the object. Reducing the number of steps can effectively alleviate this issue.

        In summary, due to Unity's simulation characteristics, controlling the robot's movement won't be straightforward. Therefore, multiple attempts and adjustments to the parameters are required. Below is a simple movement example that has a lot of room for adjustment.
    """
    robot.TurnLeft(90, 8)
    env.step(500)
    
    robot.StopMovement()
    env.step(30)
    
    robot.TurnRight(90, 8)
    env.step(500)
    
    robot.StopMovement()
    env.step(30)
    
    robot.MoveForward(0.6, 0.2)
    env.step(300)


    # Additional simulation logic can be added here
    # For example:
    # print("Force", sponge.GetForce())
    env.step()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run RCareWorld bathing environment simulation.')
    parser.add_argument('-g', '--graphics', action='store_true', help='Enable graphics')
    args = parser.parse_args()
    _main(use_graphics=args.graphics)
