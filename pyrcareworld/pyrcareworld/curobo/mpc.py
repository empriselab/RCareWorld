import os
import sys
import time
import random
import numpy as np
import torch
import math
from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.geom.types import WorldConfig
from curobo.geom.sdf.world import CollisionCheckerType
from curobo.geom.types import WorldConfig
from curobo.rollout.rollout_base import Goal
from curobo.wrap.reacher.mpc import MpcSolver, MpcSolverConfig
from pyrcareworld.envs.base_env import RCareWorld

class KinovaCuRoboMPCTracker:
    def __init__(self):
        # Initialize RCareWorld and robot
        print("Initializing RCareWorld environment...")
        self.env = RCareWorld()
        self.env.step(10)
        self.robot = self.env.GetAttr(315893)
        self.env.step(10)
        self.robot.SetPosition([0, 0, 0])
        self.env.step(10)

        print("Setting initial robot pose...")
        self.robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        self.robot.WaitDo()
        self.env.step(10)
        print("Initialization complete!")

        # Initialize CuRobo MPC
        self.tensor_args = TensorDeviceType()
        
        print("Initializing CuRobo MPC controller...")
        robot_file = "franka.yml"  # Using Franka model as a substitute for Kinova
        world_file = "collision_table.yml"

        mpc_config = MpcSolverConfig.load_from_robot_config(
            robot_file,
            world_file,
            use_cuda_graph=True,
            use_cuda_graph_metrics=True,
            use_cuda_graph_full_step=False,
            self_collision_check=True,
            collision_checker_type=CollisionCheckerType.PRIMITIVE,
            use_mppi=True,
            use_lbfgs=False,
            use_es=False,
            store_rollouts=True,
            step_dt=0.02,
        )
        self.mpc = MpcSolver(mpc_config)
        self.joint_names = self.mpc.rollout_fn.joint_names
        
        # Initialize robot position
        retract_cfg = self.mpc.rollout_fn.dynamics_model.retract_config.clone().unsqueeze(0)
        
        state = self.mpc.rollout_fn.compute_kinematics(
            JointState.from_position(retract_cfg, joint_names=self.joint_names)
        )
        self.current_state = JointState.from_position(retract_cfg, joint_names=self.joint_names)
        retract_pose = Pose(state.ee_pos_seq, quaternion=state.ee_quat_seq)
        goal = Goal(
            current_state=self.current_state,
            goal_state=JointState.from_position(retract_cfg, joint_names=self.joint_names),
            goal_pose=retract_pose,
        )

        self.goal_buffer = self.mpc.setup_solve_single(goal, 1)
        self.mpc.update_goal(self.goal_buffer)
        mpc_result = self.mpc.step(self.current_state, max_attempts=2)

        # Create cube object
        self.cube = self.env.GetAttr(1)  # Get cube with ID 1
        if self.cube is None:
            print("Warning: Cube with ID 1 not found, creating new cube...")
            try:
                # Try to create a new cube
                self.cube = self.env.CreateEntity("cube", "rcw::basic_shape::box", overwrite=True)
                self.cube.SetTransform(
                    position=[0.0, 0.03, 0.5],
                    scale=[0.02, 0.02, 0.02],
                )
            except Exception as e:
                print(f"Failed to create cube: {e}")
                sys.exit(1)
        
        # Set parameters for cube trajectory
        self.trajectory_params = {
            'center': [0.0, 0.03, 0.5],  # Trajectory center
            'radius_x': 0.3,             # X-axis radius
            'radius_z': 0.2,             # Z-axis radius
            'speed': 0.5,                # Movement speed (radians/s)
            'current_angle': 0,          # Current angle
            'target_height': 0.03,       # Target height (Y value)
        }
        
        print("CuRobo MPC initialization complete.")

    def get_joint_state(self):
        """Get current robot joint state"""
        joint_pos_deg = self.robot.data['joint_positions']
        joint_pos_rad = [np.deg2rad(x) for x in joint_pos_deg]
        return JointState.from_position(
            torch.tensor(joint_pos_rad, dtype=torch.float32, device=self.tensor_args.device).unsqueeze(0), 
            joint_names=self.joint_names
        )

    def move_cube_along_trajectory(self, dt):
        """Move cube along a smooth trajectory"""
        params = self.trajectory_params
        
        # Update current angle
        params['current_angle'] += params['speed'] * dt
        
        # Calculate new position (elliptical trajectory)
        x = params['center'][0] + params['radius_x'] * math.cos(params['current_angle'])
        y = params['target_height']
        z = params['center'][2] + params['radius_z'] * math.sin(params['current_angle'])
        
        # Set cube position
        self.cube.SetTransform(
            position=[x, y, z],
            scale=[0.02, 0.02, 0.02],
        )
        
        # Return new position
        return [x, y, z]

    def update_mpc_goal(self, target_position):
        """Update MPC controller's target position"""
        # Convert to curobo coordinate system
        target_pos_curobo = target_position.copy()
        target_pos_curobo[1] += 0.1  # Y-axis offset to keep robot end above cube
        
        # Use current orientation
        target_quat_curobo = [1, 0, 0, 0]  # Default orientation
        
        # Update goal
        ik_goal = Pose(
            position=self.tensor_args.to_device(torch.tensor(target_pos_curobo, dtype=torch.float32)),
            quaternion=self.tensor_args.to_device(torch.tensor(target_quat_curobo, dtype=torch.float32)),
        )
        self.goal_buffer.goal_pose.copy_(ik_goal)
        self.mpc.update_goal(self.goal_buffer)
        
        return target_pos_curobo

    def execute_step(self, current_joint_state, target_joint_positions):
        """Execute one control step, moving robot joints to target positions"""
        # Convert to degrees
        joint_positions_deg = [np.rad2deg(x) for x in target_joint_positions.cpu().numpy()[0]]
        
        # Get end effector position from robot data
        ee_position = self.robot.data['position']
        
        # Send control commands to robot using IKTargetDoMove
        self.robot.IKTargetDoMove(
            position=ee_position,
            duration=0.5,  # Use a reasonable duration
            speed_based=False
        )
        
        # Wait for action to complete
        self.robot.WaitDo()
        self.env.step(5)  # Let environment run for a few steps

    def run(self, max_iterations=1000, dt=0.05):
        """Run MPC tracking control main loop"""
        print(f"Starting tracking control, will run {max_iterations} iterations...")
        
        try:
            for i in range(max_iterations):
                print(f"\nStarting cycle {i+1}...")
                
                # Phase 1: Move cube to new position
                print("Moving cube to new position...")
                cube_pos = self.move_cube_along_trajectory(dt)
                self.env.step(100)  # Wait for cube movement to complete
                
                # Phase 2: Move robot above cube
                print("Moving robot above cube...")
                target_pos = self.update_mpc_goal(cube_pos)
                current_joint_state = self.get_joint_state()
                mpc_result = self.mpc.step(current_joint_state, max_attempts=1)
                
                if hasattr(mpc_result, 'action') and mpc_result.action is not None:
                    self.execute_step(current_joint_state, mpc_result.action.position)
                    self.env.step(1000)  # Wait for robot movement to complete
                
                # Phase 3: Move cube to new position
                print("Moving cube to new position...")
                cube_pos = self.move_cube_along_trajectory(dt)
                self.env.step(100)  # Wait for cube movement to complete
                
                # Phase 4: Robot follows to new position
                print("Robot following to new position...")
                target_pos = self.update_mpc_goal(cube_pos)
                current_joint_state = self.get_joint_state()
                mpc_result = self.mpc.step(current_joint_state, max_attempts=1)
                
                if hasattr(mpc_result, 'action') and mpc_result.action is not None:
                    self.execute_step(current_joint_state, mpc_result.action.position)
                    self.env.step(1000)  # Wait for robot movement to complete
                
                print(f"Cycle {i+1} completed!")
                
                # Add a short pause between cycles
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            print("\nExecution interrupted by user")
        finally:
            print("Cleaning up resources...")
            self.close()
            
    def close(self):
        """Close environment and release resources"""
        self.env.close()
        print("Environment closed!")

if __name__ == "__main__":
    print("Starting Kinova CuRobo MPC tracking demonstration...")
    
    try:
        tracker = KinovaCuRoboMPCTracker()
        tracker.run(max_iterations=1000, dt=0.05)
    except Exception as e:
        print(f"Error occurred during execution: {e}")
    
    print("Demonstration completed!")