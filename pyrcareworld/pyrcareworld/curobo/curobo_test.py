import numpy as np
import time
import random
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import os
import torch

# Curobo imports
from curobo.geom.types import WorldConfig
from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.wrap.reacher.motion_gen import (
    MotionGen,
    MotionGenConfig,
    MotionGenPlanConfig,
    PoseCostMetric,
)

class KinovaCuroboGrasp:
    def __init__(self):
        print("Initializing KinovaCuroboGrasp...")
        if not os.path.exists('/usr/lib/libdl.so'):
            print("Warning: libdl.so not found, may need to install libc6-dev package")
        
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
        
        print("Initializing Curobo motion planner...")
        self.tensor_args = TensorDeviceType()
        self.motion_gen_config = MotionGenConfig.load_from_robot_config(
            "kinova_gen3.yml",
            "collision_table.yml",
            self.tensor_args,
            trajopt_tsteps=32,
            interpolation_dt=0.02,
            collision_cache={"obb": 10, "mesh": 10},
        )
        self.motion_gen = MotionGen(self.motion_gen_config)
        self.motion_gen.warmup()
        
        self.world_coll_checker = self.motion_gen_config.world_coll_checker
        
        print("Setting initial robot pose...")
        self.robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        self.robot.WaitDo()
        self.env.step(10)
        
        print("Opening gripper...")
        self.gripper.GripperOpen()
        self.env.step(50)
        print("Initialization complete!")
        
    def create_boxes(self):
        """Create two boxes"""
        print("Creating boxes...")
        
        try:
            original_cube = self.env.GetAttr(1)
            print(f"Got original cube: {original_cube}")
        except Exception as e:
            print(f"Failed to get original cube: {e}")
            return None, None, None, None
        
        try:
            print("Creating first box...")
            box1 = original_cube.Copy(111111)
            position1 = [random.uniform(-0.5, -0.3), 0.03, random.uniform(0.3, 0.5)]
            print(f"Setting box1 position: {position1}")
            box1.SetTransform(
                position=position1,
                scale=[0.02, 0.02, 0.02],
            )
            print(f"Box1 created: {box1}")
        except Exception as e:
            print(f"Failed to create box1: {e}")
            return None, None, None, None
            
        try:
            print("Creating second box...")
            box2 = original_cube.Copy(222222)
            position2 = [random.uniform(0.3, 0.5), 0.03, random.uniform(0.3, 0.5)]
            print(f"Setting box2 position: {position2}")
            box2.SetTransform(
                position=position2,
                scale=[0.02, 0.02, 0.02],
            )
            print(f"Box2 created: {box2}")
        except Exception as e:
            print(f"Failed to create box2: {e}")
            return None, None, None, None
        
        self.env.step(200)
        print("Boxes created successfully!")
        
        self.update_collision_objects([box1, box2])
        
        return box1, box2, position1, position2

    def update_collision_objects(self, objects):
        """Update collision objects in the scene"""
        print("Updating collision objects...")
        
        world_config = WorldConfig.from_dict({
            "cuboid": {
                f"box_{obj.id}": {
                    "dims": [0.02, 0.02, 0.02],
                    "pose": [
                        obj.data['position'][0],
                        obj.data['position'][1],
                        obj.data['position'][2],
                        1.0, 0.0, 0.0, 0.0
                    ]
                }
                for obj in objects
            }
        })
        
        self.motion_gen.update_world(world_config)
        print("Collision objects updated!")
            
    def pick_and_place(self):
        """Execute pick and place operation"""
        print("Starting pick and place cycle...")
        
        box1, box2, position1, position2 = self.create_boxes()
        if box1 is None or box2 is None:
            print("Failed to create boxes, skipping cycle")
            return
            
        grab_pos = [position1[0], position1[1] + 0.1, position1[2]]
        grab_quat = [0.0, 0.0, 0.0, 1.0]
        
        grab_trajectory = self.plan_motion(grab_pos, grab_quat)
        if grab_trajectory is None:
            print("Failed to plan grab motion")
            return
            
        if not self.execute_trajectory(grab_trajectory):
            print("Failed to execute grab motion")
            return
            
        self.gripper.GripperClose()
        self.env.step(50)
        
        place_pos = [position2[0], position2[1] + 0.1, position2[2]]
        place_quat = [0.0, 0.0, 0.0, 1.0]
        
        place_trajectory = self.plan_motion(place_pos, place_quat)
        if place_trajectory is None:
            print("Failed to plan place motion")
            return
            
        if not self.execute_trajectory(place_trajectory):
            print("Failed to execute place motion")
            return
            
        self.gripper.GripperOpen()
        self.env.step(50)
        
        box1.Destroy()
        box2.Destroy()
        self.env.step(10)
        
        print("Pick and place cycle completed")
        
    def run(self, num_cycles=1):
        """Run pick and place cycles for specified number of times"""
        print(f"Starting {num_cycles} pick and place cycles...")
        try:
            for i in range(num_cycles):
                print(f"\nStarting cycle {i+1}...")
                self.pick_and_place()
                time.sleep(1)
        finally:
            print("Closing environment...")
            self.close()
            
    def close(self):
        """Close the environment"""
        self.env.close()
        print("Environment closed!")

    def plan_motion(self, target_pos, target_quat):
        """Plan motion using Curobo"""
        print("Starting motion planning...")
        
        current_joint_state = self.robot.data['joint_positions']
        print(f"Current joint state (degrees): {current_joint_state}")
        
        joint_state_rad = [np.deg2rad(x) for x in current_joint_state]
        joint_state_tensor = torch.as_tensor(joint_state_rad, device=self.tensor_args.device, dtype=self.tensor_args.dtype).unsqueeze(0)
        
        position = torch.as_tensor(target_pos, device=self.tensor_args.device, dtype=self.tensor_args.dtype).unsqueeze(0)
        quaternion = torch.as_tensor(target_quat, device=self.tensor_args.device, dtype=self.tensor_args.dtype).unsqueeze(0)
        target_pose = Pose(position=position, quaternion=quaternion)
        
        result = self.motion_gen.plan_single(
            start_state=JointState.from_position(joint_state_tensor),
            goal_pose=target_pose
        )
        
        if result.success:
            print("Motion planning successful")
            return result.optimized_plan
        else:
            print("Motion planning failed")
            return None

    def execute_trajectory(self, trajectory):
        """Execute Curobo generated trajectory"""
        print("Starting trajectory execution...")
        
        if trajectory is None:
            print("Empty trajectory, cannot execute")
            return False
                
        joint_positions = trajectory.position.cpu().numpy()
        
        for i, joint_pos in enumerate(joint_positions):
            if i % 4 != 0 and i != len(joint_positions)-1:
                continue
                
            joint_tensor = torch.tensor([joint_pos], device=self.tensor_args.device, dtype=self.tensor_args.dtype)
            
            ee_state = self.motion_gen.rollout_fn.compute_kinematics(JointState.from_position(joint_tensor))
            
            ee_pos = ee_state.ee_pos_seq.cpu().numpy()[0]
            
            self.robot.IKTargetDoMove(
                position=ee_pos.tolist(),
                duration=0.5,
                speed_based=False
            )
            
            ee_quat = ee_state.ee_quat_seq.cpu().numpy()[0]
            
            self.robot.WaitDo()
            self.env.step(5)
                
        print("Trajectory execution completed")
        return True

if __name__ == "__main__":
    print("Starting KinovaCuroboGrasp program...")
    controller = KinovaCuroboGrasp()
    controller.run(num_cycles=1)
    print("Program execution completed!")