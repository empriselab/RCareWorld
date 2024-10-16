import json
from pyrcareworld.envs.bathing_env import BathingEnv
import numpy as np
import cv2
import argparse


def _main(dev):
    '''
    Runs the simulation to allow a developer to verify the sponge's force values from the Unity editor.

    Note: This script requires the Unity Editor / EmPRISE Lab internal version of RCareWorld to be installed; for regular users, this will not work.
    '''
    # Initialize the environment
    if dev:
        env = BathingEnv(executable_file="@editor")
    else:
        print("This script requires the Unity Editor / EmPRISE Lab internal version of RCareWorld to be installed; for regular users, this will not work. However, you can fowllow the code to see how to access the sponge's force values.")
        exit(1)
    print(env.attrs)

    sponge = env.get_sponge()

    # Read collision output.
    for _ in range(9000):
        force = sponge.GetForce()
        env.step()

        print(force)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run RCareWorld bathing environment simulation.')
    parser.add_argument('-d', '--dev', action='store_true', help='Run in developer mode')
    args = parser.parse_args()
    _main(use_graphics=args.dev)
    _main()
