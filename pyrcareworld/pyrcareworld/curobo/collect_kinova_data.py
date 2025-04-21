import numpy as np
import time
import random
import h5py
import os
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import torch
from tqdm import tqdm

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

class KinovaDataCollector:
    def __init__(self, data_dir="./data/kinova_data", num_episodes=1000, episode_length=100):
        print("Initializing KinovaDataCollector...")
        
        # Create data directory
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize environment parameters
        self.num_episodes = num_episodes
        self.episode_length = episode_length
        
        # Initialize RCareWorld environment
        self.env = RCareWorld()
        self.env.step(10)
        
        # Create Kinova robot instance
        self.robot = self.env.GetAttr(315893)
        self.env.step(10)
        
        # Use fixed, stable initial position
        self.robot.SetPosition([0, 0, 0])
        self.env.step(20)  # Increase steps to ensure position is set
        
        # Initialize Curobo motion planner
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
        
        # Set to a good, stable initial pose, clearly above workspace
        safe_initial_position = [0, 0.5, 0.7]  # Increase height to avoid pointing at ground
        self.robot.IKTargetDoMove(position=safe_initial_position, duration=1.0, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 0, 180], duration=1.0, speed_based=False)  # Adjust rotation angle
        self.robot.WaitDo()
        self.env.step(30)  # Increase steps to ensure pose is set
        
        print("Initialization complete!")

    def create_target_cube(self, position):
        """Create target cube at specified position"""
        try:
            original_cube = self.env.GetAttr(1)
            target_cube = original_cube.Copy(111111)
            
            # Ensure y coordinate is increased by 1
            adjusted_position = [position[0], position[1] + 1.0, position[2]]
            
            target_cube.SetTransform(
                position=adjusted_position,
                scale=[0.02, 0.02, 0.02],
            )
            self.env.step(50)
            return target_cube
        except Exception as e:
            print(f"Failed to create target cube: {e}")
            return None

    def get_random_position(self, base_position, radius=0.1):
        """Generate a random position near the base position"""
        x = base_position[0] + random.uniform(-radius, radius)
        y = base_position[1]
        z = base_position[2] + random.uniform(-radius, radius)
        return [x, y, z]

    def get_robot_state(self):
        """Get robot state"""
        # Get joint states
        joint_positions = np.array(self.robot.data['joint_positions'])
        joint_velocities = np.array(self.robot.data['joint_velocities'])
        
        # Get end-effector states
        ee_position = np.array(self.robot.data['position'])
        ee_rotation = np.array(self.robot.data['rotation'])
        
        return {
            'joint_positions': joint_positions,
            'joint_velocities': joint_velocities,
            'ee_position': ee_position,
            'ee_rotation': ee_rotation
        }

    def plan_motion(self, target_pos, target_quat, plan_config=None):
        """Plan motion using Curobo with optional planning config"""
        current_joint_state = self.robot.data['joint_positions']
        joint_state_rad = [np.deg2rad(x) for x in current_joint_state]
        joint_state_tensor = torch.as_tensor(joint_state_rad, device=self.tensor_args.device, dtype=self.tensor_args.dtype).unsqueeze(0)
        
        position = torch.as_tensor(target_pos, device=self.tensor_args.device, dtype=self.tensor_args.dtype).unsqueeze(0)
        quaternion = torch.as_tensor(target_quat, device=self.tensor_args.device, dtype=self.tensor_args.dtype).unsqueeze(0)
        target_pose = Pose(position=position, quaternion=quaternion)
        
        if plan_config is None:
            result = self.motion_gen.plan_single(
                start_state=JointState.from_position(joint_state_tensor),
                goal_pose=target_pose
            )
        else:
            result = self.motion_gen.plan_single(
                start_state=JointState.from_position(joint_state_tensor),
                goal_pose=target_pose,
                plan_config=plan_config
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

    def move_to_target(self, target_position):
        """Move robot to target position using improved approach"""
        # Calculate safe point above target to avoid collisions
        target_pos = [target_position[0], target_position[1] + 0.15, target_position[2]]  # Increase height offset
        target_quat = [0.0, 0.0, 0.0, 1.0]
        
        # Increase planning retry attempts and tuning parameters
        plan_config = MotionGenPlanConfig(
            max_attempts=20,  # Increase attempt count
            enable_opt=True,
            enable_graph_attempt=True,
            timeout=1.0,  # Increase timeout
        )
        
        trajectory = self.plan_motion(target_pos, target_quat, plan_config)
        if trajectory is not None:
            return self.execute_trajectory(trajectory)
        return False

    def move_target_cube(self, position):
        """Move target cube to specified position instead of creating new one"""
        try:
            # Get the cube with ID 1 directly
            target_cube = self.env.GetAttr(1)
            
            # No longer add extra height offset, use position similar to working code
            adjusted_position = [position[0], 0.03, position[2]]  # Fixed y coordinate to 0.03
            
            # Set cube position and size
            target_cube.SetTransform(
                position=adjusted_position,
                scale=[0.02, 0.02, 0.02],
            )
            self.env.step(50)
            
            print(f"Moved target cube to position: {adjusted_position}")
            return target_cube, adjusted_position
        except Exception as e:
            print(f"Failed to move target cube: {e}")
            return None, None

    def collect_episode(self, episode_idx):
        """Collect data for one episode"""
        episode_data = {
            'observations': [],
            'actions': [],
            'rewards': [],
            'dones': [],
            'targets': []
        }
        
        # Use position ranges similar to working code
        if episode_idx % 2 == 0:
            # Use cube1 position range from working code
            base_position = [-0.4, 0.03, 0.4]
        else:
            # Use cube2 position range from working code
            base_position = [0.4, 0.03, 0.4]
        
        random_position = self.get_random_position(base_position, radius=0.1)
        target_cube, actual_position = self.move_target_cube(random_position)
        
        if target_cube is None or actual_position is None:
            print(f"Failed to move target cube for episode {episode_idx}")
            return None
        
        # Use actual cube position as target
        target_position = actual_position
        
        # Important: No longer reset robot position every time, maintain a safe, stable pose
        # Only reset position on first episode or after planning failures
        if episode_idx == 0 or episode_idx % 10 == 0:
            # Reset to safe position
            safe_initial_position = [0, 0.5, 0.7]
            self.robot.IKTargetDoMove(position=safe_initial_position, duration=1.0, speed_based=False)
            self.robot.IKTargetDoRotate(rotation=[0, 0, 180], duration=1.0, speed_based=False)
            self.robot.WaitDo()
            self.env.step(20)
            print(f"Reset robot to safe position in episode {episode_idx}")
        
        # Add safety margin during motion planning
        print(f"Planning motion to target at {target_position}")
        success = self.move_to_target(target_position)
        
        if not success:
            print(f"Failed to execute motion in episode {episode_idx}")
            return None
        
        # Get current state and reward
        robot_state = self.get_robot_state()
        position_diff = np.array(target_position) - robot_state['ee_position']
        reward = -np.linalg.norm(position_diff)
        
        # Store data
        observation = np.concatenate([
            robot_state['joint_positions'],
            robot_state['joint_velocities'],
            robot_state['ee_position'],
            robot_state['ee_rotation'],
            target_position,
            [0, 0, 0, 1]  # target rotation (identity quaternion)
        ])
        
        # Define action as the movement required to reach the target
        action = position_diff
        
        episode_data['observations'].append(observation)
        episode_data['actions'].append(action)
        episode_data['rewards'].append(reward)
        episode_data['dones'].append(1)  # Mark as end
        episode_data['targets'].append(np.concatenate([
            target_position,
            [0, 0, 0, 1]  # target rotation
        ]))
        
        # Convert to numpy arrays
        for key in episode_data:
            episode_data[key] = np.array(episode_data[key])
        
        return episode_data

    def collect_data(self):
        """Collect data for all episodes"""
        all_episodes = []
        
        for episode_idx in tqdm(range(self.num_episodes)):
            episode_data = self.collect_episode(episode_idx)
            if episode_data is not None:
                all_episodes.append(episode_data)
                print(f"Successfully collected episode {episode_idx}")
            else:
                print(f"Failed to collect episode {episode_idx}")
                    
        # Save data
        if len(all_episodes) > 0:
            self.save_data(all_episodes)
            print(f"Collected {len(all_episodes)} successful episodes out of {self.num_episodes} attempts")
        else:
            print("No successful episodes were collected")
        
    def save_data(self, episodes):
        """Save collected data"""
        # Create HDF5 file
        file_path = os.path.join(self.data_dir, 'kinova_data.hdf5')
        with h5py.File(file_path, 'w') as f:
            # Create group
            grp = f.create_group('data')
            
            # Save each episode
            for i, episode in enumerate(episodes):
                ep_grp = grp.create_group(f'episode_{i}')
                for key, value in episode.items():
                    ep_grp.create_dataset(key, data=value)
                    
        print(f"Data saved to {file_path}")
        
    def close(self):
        """Close environment"""
        self.env.close()
        print("Environment closed!")

if __name__ == "__main__":
    print("Starting data collection...")
    collector = KinovaDataCollector(
        data_dir="./data/kinova_data",
        num_episodes=1000,
        episode_length=1000
    )
    
    try:
        collector.collect_data()
    finally:
        collector.close()
    print("Data collection completed!") 