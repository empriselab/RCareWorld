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

class KinovaCuroboMove:
    def __init__(self):
        print("Initializing KinovaCuroboMove...")
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
        
        print("Initializing Curobo motion planner...")
        self.tensor_args = TensorDeviceType()
        self.motion_gen_config = MotionGenConfig.load_from_robot_config(
            "kinova_gen3.yml",
            "collision_table.yml",
            self.tensor_args,
            trajopt_tsteps=32,
            interpolation_dt=0.01,
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
        print("Initialization complete!")

    def create_cube(self, cube_id, position):
        """Create a cube at specified position"""
        try:
            original_cube = self.env.GetAttr(1)
            cube = original_cube.Copy(cube_id)
            cube.SetTransform(
                position=position,
                scale=[0.02, 0.02, 0.02],
            )
            self.env.step(50)
            return cube
        except Exception as e:
            print(f"Failed to create cube: {e}")
            return None

    def get_random_position(self, base_position, radius=0.1):
        """Generate a random position near the base position"""
        x = base_position[0] + random.uniform(-radius, radius)
        y = base_position[1]
        z = base_position[2] + random.uniform(-radius, radius)
        return [x, y, z]

    def plan_motion(self, target_pos, target_quat):
        """Plan motion using Curobo"""
        current_joint_state = self.robot.data['joint_positions']
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
            return result.optimized_plan
        else:
            print("Motion planning failed")
            return None

    def execute_trajectory(self, trajectory):
        """Execute Curobo generated trajectory"""
        if trajectory is None:
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
            
            self.robot.WaitDo()
            self.env.step(5)
                
        return True

    def move_to_cube(self, cube_position):
        """Move robot to position above cube"""
        target_pos = [cube_position[0], cube_position[1] + 0.1, cube_position[2]]
        target_quat = [0.0, 0.0, 0.0, 1.0]
        
        trajectory = self.plan_motion(target_pos, target_quat)
        if trajectory is not None:
            return self.execute_trajectory(trajectory)
        return False

    def run(self, num_cycles=10):
        """Run the continuous movement cycle"""
        print(f"Starting {num_cycles} movement cycles...")
        
        # Initial positions for cubes
        cube1_pos = [-0.4, 0.03, 0.4]
        cube2_pos = [0.4, 0.03, 0.4]
        
        # Create initial cubes
        cube1 = self.create_cube(111111, cube1_pos)
        cube2 = self.create_cube(222222, cube2_pos)
        
        if cube1 is None or cube2 is None:
            print("Failed to create initial cubes")
            return
            
        try:
            for i in range(num_cycles):
                print(f"\nStarting cycle {i+1}...")
                
                # Move to cube1
                print("Moving to cube1...")
                if not self.move_to_cube(cube1_pos):
                    print("Failed to move to cube1")
                    continue
                    
                # Delete and recreate cube2
                print("Regenerating cube2...")
                cube2.Destroy()
                self.env.step(10)
                cube2_pos = self.get_random_position(cube2_pos)
                cube2 = self.create_cube(222222, cube2_pos)
                
                # Move to cube2
                print("Moving to cube2...")
                if not self.move_to_cube(cube2_pos):
                    print("Failed to move to cube2")
                    continue
                    
                # Delete and recreate cube1
                print("Regenerating cube1...")
                cube1.Destroy()
                self.env.step(10)
                cube1_pos = self.get_random_position(cube1_pos)
                cube1 = self.create_cube(111111, cube1_pos)
                
                time.sleep(1)
                
        finally:
            print("Cleaning up...")
            if cube1:
                cube1.Destroy()
            if cube2:
                cube2.Destroy()
            self.env.step(10)
            self.close()
            
    def close(self):
        """Close the environment"""
        self.env.close()
        print("Environment closed!")

if __name__ == "__main__":
    print("Starting KinovaCuroboMove program...")
    controller = KinovaCuroboMove()
    controller.run(num_cycles=10)
    print("Program execution completed!")