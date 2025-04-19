import numpy as np
import time
import random
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import os
import cv2

def save_and_read_image(camera, filename):
    with open(filename, 'wb') as f:
        f.write(camera.data["rgb"])
    image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    return image

class KinovaLimbDataCollector:
    def __init__(self):
        print("Initializing KinovaCuroboGrasp...")
        if not os.path.exists('/usr/lib/libdl.so'):
            print("Warning: libdl.so not found, may need to install libc6-dev package")
        
        self.prefix = "data_0417/"
        
        print("Initializing RCareWorld environment...")
        self.env = RCareWorld()
        self.env.step(10)
        
        print("Creating Kinova robot instance...")
        self.robot = self.env.GetAttr(315893)
        self.env.step(10)
        
        print("Setting initial robot position...")
        self.robot.SetPosition([0, 0, 0])
        self.env.step(10)
        
        print("Getting gripper controller...")
        self.gripper = self.env.GetAttr(3158930)
        self.env.step(10)
        
        print("Setting initial robot pose...")
        self.robot.IKTargetDoMove(position=[0, 0.2, 0.2], duration=0, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        self.robot.WaitDo()
        self.env.step(10)
        
        print("Opening gripper...")
        self.gripper.GripperOpen()
        self.env.step(50)
        print("Initialization complete!")

        print("Getting the camera...")
        self.camera = self.env.GetAttr(4356)
        self.env.step(10)
        print("Camera initialized!")

        print("Getting the Upper Arm...")
        self.upper_arm = self.env.GetAttr(234567)
        print("Upper Arm initialized!")

        print("Getting the Lower Arm...")
        self.lower_arm = self.env.GetAttr(234568)
        print("Lower Arm initialized!")

        # self.env.Pend()

    def collect_data(self, trial_id=0):
        print("Collecting data...")
        
        # Before 
        # print(self.upper_arm.data)
        # print(self.lower_arm.data)
        self.camera.GetRGB(width=512, height=512)
        self.env.step()

        # Save and read the captured image using current time using time.time()
        # Generate a timestamped filename
        timestamp = time.time()
        filename = f"{self.prefix}{trial_id}_before_image_{timestamp:.0f}.png"

        # Save and read the image
        image = save_and_read_image(self.camera, filename)

        # Save before state as json
        # Upper arm data as json
        with open(f"{self.prefix}{trial_id}_before_upper_arm_data_{timestamp:.0f}.json", "w") as f:
            f.write(str(self.upper_arm.data))
        # Lower arm data as json
        with open(f"{self.prefix}{trial_id}_before_lower_arm_data_{timestamp:.0f}.json", "w") as f:
            f.write(str(self.lower_arm.data))

        # randomize robot action from -0.2 to 0.2
        rand_action = random.uniform(-0.4, 0.4)
        # save the action as json
        with open(f"{self.prefix}{trial_id}_action_{timestamp:.0f}.json", "w") as f:
            f.write(str(rand_action))

        self.robot.IKTargetDoMove(position=[rand_action, 0, rand_action], duration=2, speed_based=False, relative=True)
        self.robot.WaitDo()
        for i in range(10):
            self.env.step(9)
            self.camera.GetRGB(width=512, height=512)
            self.env.step()
            timestamp = time.time()
            filename = f"{self.prefix}{trial_id}_during_image_{timestamp:.0f}.png"

            # Save and read the image
            image = save_and_read_image(self.camera, filename)
        
        # After
        with open(f"{self.prefix}{trial_id}_after_upper_arm_data_{timestamp:.0f}.json", "w") as f:
            f.write(str(self.upper_arm.data))
        # Lower arm data as json
        with open(f"{self.prefix}{trial_id}_after_lower_arm_data_{timestamp:.0f}.json", "w") as f:
            f.write(str(self.lower_arm.data))
        self.camera.GetRGB(width=512, height=512)
        self.env.step()
        timestamp = time.time()
        filename = f"{self.prefix}{trial_id}_after_image_{timestamp:.0f}.png"

        # Save and read the image
        image = save_and_read_image(self.camera, filename)


        self.robot.IKTargetDoMove(position=[0, 0.2, 0.2], duration=0, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        self.robot.WaitDo()
        self.env.step(10)

        self.upper_arm.SetPosition([0.658999979,0.0700000003,0.282999992])
        self.upper_arm.SetRotation([0, 0, -90])

        self.lower_arm.SetPosition([0.0719999075,0.0700000599,0.282999992])
        self.lower_arm.SetRotation([0, 0, -90])
        self.env.step(5)
        
    

if __name__ == "__main__":
    print("Starting KinovaCuroboGrasp program...")
    collector = KinovaLimbDataCollector()
    for i in range(1000):
        collector.collect_data(i)