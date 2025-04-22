import os
import sys
import time
import numpy as np
import torch
import math
from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.geom.types import WorldConfig
from curobo.geom.sdf.world import CollisionCheckerType
from curobo.rollout.rollout_base import Goal
from curobo.wrap.reacher.mpc import MpcSolver, MpcSolverConfig
from pyrcareworld.envs.base_env import RCareWorld

class KinovaCuRoboTracker:
    """
    A class that implements a Kinova robot tracking a cube using CuRobo's MPC controller.
    Similar to the Storm-kit implementation but using CuRobo API instead.
    """
    
    def __init__(self, robot_file="kinova_gen3.yml", world_file="collision_table.yml", move_cube=False):
        """
        Initialize the Kinova CuRobo tracker.
        
        Args:
            robot_file: Configuration file for the robot
            world_file: Configuration file for the world
            move_cube: Whether the cube should move automatically
        """
        # Initialize RCare environment
        self.env = RCareWorld()
        self.env.step(10)
        self.robot = self.env.GetAttr(315893)  # Get robot by ID
        self.env.step(10)
        
        # Initialize tensor arguments for CuRobo
        self.tensor_args = TensorDeviceType(device="cuda:0", dtype=torch.float32)
        
        # Initialize MPC controller
        self.setup_mpc_controller(robot_file, world_file)
        
        # Create the cube object
        self.setup_cube_objects()
        
        # Initialize trajectory parameters
        self.trajectory_params = {
            'center': [0.0, 0.05, 0.5],  # 轨迹中心
            'radius': 0.3,               # 圆形轨迹半径
            'speed': 0.5,                # 移动速度（弧度/秒）
            'current_angle': 0,          # 当前角度
            'target_height': 0.05,       # 目标高度（Y值）
            'move_cube': move_cube       # 是否移动cube
        }
        
        # Set initial position
        self.set_initial_position()
    
    def setup_mpc_controller(self, robot_file, world_file):
        """Setup the CuRobo MPC controller"""
        print("Initializing CuRobo MPC controller...")
        
        # Create MPC configuration
        mpc_config = MpcSolverConfig.load_from_robot_config(
            robot_file,
            world_file,
            use_cuda_graph=True,
            use_cuda_graph_metrics=True,
            collision_checker_type=CollisionCheckerType.PRIMITIVE,
            self_collision_check=True,
            collision_activation_distance=0.03,
            use_mppi=True,
            use_lbfgs=False,
            use_es=False,
            step_dt=0.02,
            store_rollouts=True,
        )
        
        # Create MPC solver
        self.mpc = MpcSolver(mpc_config)
        
        # Get joint names
        self.joint_names = self.mpc.rollout_fn.joint_names
        print(f"Robot joint names: {self.joint_names}")
        
        # Get retract configuration
        self.retract_cfg = self.mpc.rollout_fn.dynamics_model.retract_config.clone().unsqueeze(0)
        
        # Initialize current state
        self.current_state = JointState.from_position(self.retract_cfg, joint_names=self.joint_names)
        
        # Initialize goal buffer
        state = self.mpc.rollout_fn.compute_kinematics(self.current_state)
        retract_pose = Pose(state.ee_pos_seq, quaternion=state.ee_quat_seq)
        
        goal = Goal(
            current_state=self.current_state,
            goal_state=JointState.from_position(self.retract_cfg, joint_names=self.joint_names),
            goal_pose=retract_pose,
        )
        
        self.goal_buffer = self.mpc.setup_solve_single(goal, 1)
        self.mpc.update_goal(self.goal_buffer)
        
        # Do an initial step
        mpc_result = self.mpc.step(self.current_state, max_attempts=2)
        
        print("CuRobo MPC controller initialized.")
    
    def setup_cube_objects(self):
        """Create the cube objects in the environment"""
        print("Creating cube objects...")
        
        # Try to get the original cube
        self.cube = self.env.GetAttr(1)
        
        # If original cube not found, create a new one
        if self.cube is None:
            try:
                self.cube = self.env.CreateEntity("cube", "rcw::basic_shape::box", overwrite=True)
                self.cube.SetTransform(
                    position=[0.0, 0.5, 0.5],
                    scale=[0.05, 0.05, 0.05],
                )
            except Exception as e:
                print(f"Failed to create cube: {e}")
                sys.exit(1)
        
        # Create a copy of the cube for movement
        self.moving_cube = self.cube.Copy(111111)  # unique ID
        self.moving_cube.SetTransform(
            position=[0.0, 0.05, 0.5],
            scale=[0.05, 0.05, 0.05],
        )
        self.env.step(20)
        
        print("Cube objects created.")
    
    def set_initial_position(self):
        """Set the initial position of the robot"""
        print("Setting initial robot position...")
        
        self.robot.EnabledNativeIK(False)
        self.env.step()
        # Move robot to initial position
        self.robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0.5, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 0, 180], duration=0.5, speed_based=False)
        self.robot.WaitDo()
        self.env.step(50)

        self.robot.EnabledNativeIK(True)
        self.env.step()
        
        print("Initial position set.")
    
    def get_robot_state(self):
        """Get current robot joint state"""
        try:
            # Get joint positions in degrees and convert to radians
            joint_positions = np.radians(np.array(self.robot.data['joint_positions']) % 360.)
            
            # Normalize joint angles to [-pi, pi]
            for i in range(len(joint_positions)):
                if joint_positions[i] > np.pi:
                    joint_positions[i] = joint_positions[i] - (2 * np.pi)
            
            # Create JointState for CuRobo
            joint_state = JointState.from_position(
                torch.tensor(joint_positions, device=self.tensor_args.device, dtype=self.tensor_args.dtype).unsqueeze(0),
                joint_names=self.joint_names
            )
            
            # Compute forward kinematics
            state = self.mpc.rollout_fn.compute_kinematics(joint_state)
            
            return joint_state, state
            
        except Exception as e:
            print(f"Error in get_robot_state: {e}")
            raise
    
    def calculate_cube_position(self, dt):
        """Calculate new position for the cube along trajectory"""
        params = self.trajectory_params
        
        if not params['move_cube']:
            return self.moving_cube.data['position']
            
        # 更新当前角度
        params['current_angle'] += params['speed'] * dt
        
        # 计算新位置（圆形轨迹）
        x = params['center'][0] + params['radius'] * math.cos(params['current_angle'])
        y = params['target_height']
        z = params['center'][2] + params['radius'] * math.sin(params['current_angle'])
        
        return [x, y, z]
    
    def update_cube_position(self, position):
        """Update the cube position in the environment"""
        self.moving_cube.SetTransform(
            position=position,
            scale=[0.05, 0.05, 0.05],
        )
        self.env.step(1)  # Small step to update visuals
        return position
    
    def update_target_pose(self, position):
        """Update MPC controller's target position"""
        try:
            # Create target pose
            # Adjust for height to position end-effector above the cube
            target_position = position.copy()
            target_position = [-target_position[0], -target_position[2], target_position[1]]
            # target_position[1] += 0.2  # Offset in Y direction (height)
            
            # Default downward-facing orientation (adjust as needed)
            target_quaternion = [0, 0, 1, 0]  # Orientation pointing downward
            
            # Create pose object
            target_pose = Pose(
                position=torch.tensor(target_position, device=self.tensor_args.device, dtype=self.tensor_args.dtype),
                quaternion=torch.tensor(target_quaternion, device=self.tensor_args.device, dtype=self.tensor_args.dtype),
            )
            
            # Update goal buffer
            self.goal_buffer.goal_pose.copy_(target_pose)
            self.mpc.update_goal(self.goal_buffer)
            
            return target_position
            
        except Exception as e:
            print(f"Error updating target pose: {e}")
            raise
    
    def move_robot(self, joint_positions):
        """Move robot to target joint positions"""
        try:
            # Convert to degrees for RCareWorld
            joint_positions_deg = np.degrees(joint_positions.cpu().numpy()[0])
            
            # Send control commands
            self.robot.SetJointPositionDirectly(joint_positions_deg)
            self.env.step()
            
        except Exception as e:
            print(f"Error moving robot: {e}")
            raise
    
    def step(self, dt=0.02):
        """Perform one control step"""
        try:
            cube_position = self.moving_cube.data['position']

            self.env.step()
            
            # 3. 获取当前机器人状态
            joint_state, _ = self.get_robot_state()
            
            # 4. 更新MPC的目标位置
            target_position = self.update_target_pose(cube_position)
            
            # 5. 求解MPC并获取动作
            mpc_result = self.mpc.step(joint_state, max_attempts=2)
            
            # 6. 应用动作到机器人
            if hasattr(mpc_result, 'action') and mpc_result.action is not None:
                # 打印调试信息
                print(f"\nTarget position: {target_position}")
                print(f"Current joint positions: {np.degrees(joint_state.position.cpu().numpy()[0])}")
                print(f"New joint positions: {np.degrees(mpc_result.action.position.cpu().numpy()[0])}")
                
                self.move_robot(mpc_result.action.position)
            
            # 7. 获取更新后的机器人状态
            joint_state, state = self.get_robot_state()
            
            # 8. 返回当前状态用于监控
            return {
                'cube_position': cube_position,
                'target_position': target_position,
                'current_ee_position': state.ee_pos_seq.cpu().numpy()[0],
                'current_ee_orientation': state.ee_quat_seq.cpu().numpy()[0],
                'joint_positions': joint_state.position.cpu().numpy()[0]
            }
            
        except Exception as e:
            print(f"Error in step: {e}")
            raise
    
    def close(self):
        """Close environment and release resources"""
        if hasattr(self, 'moving_cube'):
            self.moving_cube.Destroy()
        self.env.close()
        print("Environment closed")

def track_cube_demo():
    """Demo function to show cube tracking"""
    print("Starting Kinova CuRobo MPC tracking demonstration...")
    
    try:
        # Create tracker
        tracker = KinovaCuRoboTracker()
        
        # Run for some steps
        for i in range(1000):
            print(f"\nStep {i+1}:")
            
            # Perform one control step
            result = tracker.step(dt=0.02)
            
            # Print information every few steps
            if (i+1) % 10 == 0:
                print("Cube position:", result['cube_position'])
                print("Target position:", result['target_position'])
                print("Current end-effector position:", result['current_ee_position'])
                print("Position error:", np.linalg.norm(result['target_position'] - result['current_ee_position']))
            
            # Wait to visualize movement
            # time.sleep(0.05)
            
            # Check for keyboard interrupt
            if i % 10 == 0:
                sys.stdout.write("Press Ctrl+C to stop...\r")
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        print("\nDemonstration interrupted by user")
    except Exception as e:
        print(f"Error in demonstration: {e}")
    finally:
        if 'tracker' in locals():
            tracker.close()
    
    print("Demonstration completed!")

if __name__ == "__main__":
    track_cube_demo()