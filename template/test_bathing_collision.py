import json
from pyrcareworld.envs.bathing_env import BathingEnv
import numpy as np
import cv2
import argparse

def _main(use_graphics=False):
    # Initialize the environment
    env = BathingEnv(graphics=use_graphics)
    print(env.attrs)

    robot = env.get_robot()
    env.step()

    # Move forward
    robot.MoveBack(3, 0.5)

    # Read collision output.
    for _ in range(9000):
        env.GetCurrentCollisionPairs()
        env.step()

        print(env.data["collision_pairs"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run RCareWorld bathing environment simulation.')
    parser.add_argument('-g', '--graphics', action='store_true', help='Enable graphics')
    args = parser.parse_args()
    _main(use_graphics=args.graphics)
    _main()
