import json
from pyrcareworld.envs.bathing_env import BathingEnv
import numpy as np
import cv2
import argparse

def _main():
    # Initialize the environment
    env = BathingEnv(graphics=False)
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
    _main()
