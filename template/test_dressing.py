from pyrcareworld.envs.dressing_env import DressingEnv
import pyrcareworld.attributes as attr
import cv2
import os
import numpy as np
import json
import argparse

def _main(use_graphics=False):
    if use_graphics:
        text = """
        An example of the usage of the dressing environment.

        The robot will move to the first position, pick up the cloth, and move to the second position to drop the cloth.

        You can obtain low level information of the cloth, the robot, and use unlimited numbers of cameras to observe the scene.

        Check the website detailed rubric. After each run of the simulation, a json file will be generated in the current directory
        (~/.config/unity3d/RCareWorld/DressingPlayer).
        The path may be different accotding to the OS and your computer configuration.
        """
            
        print(text)
    # Initialize the environment
    env = DressingEnv(graphics=use_graphics)
    print(env.attrs)

    robot = env.get_robot()
    env.step()

    # Get the gripper attribute and open the gripper
    gripper = env.get_gripper()
    gripper.GripperOpen()
    env.step(300)

    gripper.GripperClose()
    env.step(300)

    # Get the cloth attribute and perform a simulation step
    cloth = env.get_cloth()
    print(cloth.data)

    # Camera operations: Attach a camera to the robot's hand
    camera = env.get_camera()
    camera.SetTransform(position=gripper.data['position'], rotation=[-90, 90, -90])
    camera.SetParent(3158930)
    camera.GetRGB(512, 512)
    env.step()
    rgb = np.frombuffer(camera.data["rgb"], dtype=np.uint8)
    env.step()

    # Random positions and rotation
    position1 = (1.5, 2.3, 0.6)
    rotation = (0, 0, -69.858)

    # Move the robot to the first position
    robot.IKTargetDoMove(
        position=[position1[0], position1[1], position1[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()

    rgb = cv2.imdecode(rgb, cv2.IMREAD_COLOR)
    cv2.imwrite("rgb_hand.png", rgb)

    robot.IKTargetDoRotate(
        rotation=[rotation[0], rotation[1], rotation[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()

    # Retrieve cloth particle data after moving the robot
    cloth.GetParticles()
    env.step()

    env.step(300)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run RCareWorld dressing environment simulation.')
    parser.add_argument('-g', '--graphics', action='store_true', help='Enable graphics')
    args = parser.parse_args()
    _main(use_graphics=args.graphics)
