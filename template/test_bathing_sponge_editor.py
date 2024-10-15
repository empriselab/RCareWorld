import json
from pyrcareworld.envs.bathing_env import BathingEnv
import numpy as np
import cv2
import argparse


def _main():
    '''
    Runs the simulation to allow a developer to verify the sponge's force values from the Unity editor.

    Note: This script requires the Unity Editor / EmPRISE Lab internal version of RCareWorld to be installed; for regular users, this will not work.
    '''
    # Initialize the environment
    env = BathingEnv(executable_file="@editor")
    print(env.attrs)

    sponge = env.get_sponge()

    # Read collision output.
    for _ in range(9000):
        force = sponge.GetForce()
        env.step()

        print(force)

if __name__ == "__main__":
    _main()
