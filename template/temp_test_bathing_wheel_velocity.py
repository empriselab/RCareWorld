import json
from pyrcareworld.envs.bathing_env import BathingEnv
import numpy as np
import cv2
import argparse

def _main(use_graphics=False):
    # Initialize the environment
    env = BathingEnv(executable_file="@editor")
    print(env.attrs)

    robot = env.get_robot()
    env.step()

    # Drive forward
    for _ in range(300):
        robot.TargetVelocity(0.1, 0.1)
        env.step()

    # Drive backward
    for _ in range(300):
        robot.TargetVelocity(-0.1, -0.1)
        env.step()

    # Turn Left with angular velocity control
    for _ in range(300):
        robot.TargetVelocity(-0.1, 0.1)
        env.step()

    # Turn Right with angular velocity control
    for _ in range(300):
        robot.TargetVelocity(0.1, -0.1)
        env.step()

    # Stop
    for _ in range(300):
        robot.TargetVelocity(0, 0)
        env.step()

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run RCareWorld bathing environment simulation.')
    _main()
