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
    position1 = (0.492, 0.644, 0.03)
    position2 = (0.296, 0.849, 3.168)

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
        position=[position2[0], position2[1] - 0.05, position2[2]],
        duration=4,
        speed_based=False,
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position2[0], position2[1] + 0.06, position2[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position1[0], position1[1], position1[2]+1],
        duration=2,
        speed_based=False,
    )
    env.step(300)
    
    """
        The Stretch's movement speed is related to the time in the step() method, as well as the defined distance and speed.
        
        - If the `env.step` duration is too short, it can lead to incomplete turns and might cause the robot to move too quickly.

        - If the `env.step` duration is too long, it can lead to slow drifting due to friction.

        - If the speed is too fast, it can cause the robot to move too quickly and fall apart, and it may also result in the robot jumping and falling down.

        - If the speed is too slow, it can lead to the robot not moving at all, only making slight movements, or quickly returning to its original position after moving.

        - If you observe stretching and contracting in the robot's arm, this is due to angular momentum. Reducing speed can lessen this effect. Additionally, we recommend lowering the robot's arm during movement to lower the center of gravity, effectively reducing this issue and ensuring arm stability.

        Below is a simple example where the robot can move smoothly using these parameters, though there is significant room for adjustment.

        Particularly, we do not recommend continuous motion as it can lead to great instability. It is better to interrupt and halt movement intermittently to reduce continuous motion.
    """
    robot.TurnLeft(90, 1)
    env.step(600)
    
    # robot.StopMovement()
    # env.step(30)
    
    robot.TurnRight(90, 1)
    env.step(600)
    
    # robot.StopMovement()
    # env.step(30)
    
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
