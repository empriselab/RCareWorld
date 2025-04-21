import os
import sys
import random
import numpy as np
import h5py
import time
from tqdm import tqdm
import pyrcareworld.attributes as attr
from pyrcareworld.envs.base_env import RCareWorld

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
        self.env.SetTimeStep(0.005)
        self.env.step()
        
        # Create Kinova robot instance
        self.robot = self.env.GetAttr(315893)
        self.robot.SetPosition([0, 0, 0])
        self.env.step()
        
        # Get gripper attribute and open gripper
        self.gripper = self.env.GetAttr(3158930)
        self.gripper.GripperOpen()
        
        # Move and rotate robot to initial position
        self.robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        self.robot.WaitDo()
        self.env.step(10)
        
        print("Initialization complete!")

    def get_robot_state(self):
        """Get robot state"""
        # Get joint state
        joint_positions = np.array(self.robot.data['joint_positions'])
        joint_velocities = np.array(self.robot.data['joint_velocities'])
        
        # Get end effector state
        ee_position = np.array(self.robot.data['position'])
        ee_rotation = np.array(self.robot.data['rotation'])
        
        return {
            'joint_positions': joint_positions,
            'joint_velocities': joint_velocities,
            'ee_position': ee_position,
            'ee_rotation': ee_rotation
        }

    def place_cube_at_random_position(self):
        """Get and move cube with ID 1 to random position"""
        # Get cube with ID 1
        cube = self.env.GetAttr(1)
        
        # Generate random position
        position = [random.uniform(-0.5, 0.5), 0.03, random.uniform(0.3, 0.5)]
        
        # Set cube to random position
        cube.SetTransform(
            position=position,
            scale=[0.02, 0.02, 0.02],
        )
        self.env.step(50)
        
        return cube, position

    def move_to_position(self, target_position, duration=2.0, relative=False):
        """Move to target position and collect data"""
        start_state = self.get_robot_state()
        start_position = start_state['ee_position']
        
        # Execute movement
        self.robot.IKTargetDoMove(
            position=target_position,
            duration=duration,
            speed_based=False,
            relative=relative
        )
        self.robot.WaitDo()
        
        # Collect trajectory data
        trajectory_data = []
        
        # Calculate vector to target (as action)
        if relative:
            action = np.array(target_position)
        else:
            action = np.array(target_position) - start_position
        
        # Wait for action to complete while collecting data
        steps_done = 0
        max_steps = int(duration / 0.005) * 2  # Assuming each time step is 0.005 seconds, wait slightly longer
        
        for _ in range(max_steps):
            self.env.step(1)
            steps_done += 1
            
            # Collect data every few steps (to reduce data volume)
            if steps_done % 10 == 0:
                current_state = self.get_robot_state()
                trajectory_data.append({
                    'joint_positions': current_state['joint_positions'],
                    'joint_velocities': current_state['joint_velocities'],
                    'ee_position': current_state['ee_position'],
                    'ee_rotation': current_state['ee_rotation'],
                    'action': action,
                    'done': 0  # Not done
                })
                
        # Ensure movement is completely finished
        self.robot.WaitDo()
        
        # Add final state
        final_state = self.get_robot_state()
        trajectory_data.append({
            'joint_positions': final_state['joint_positions'],
            'joint_velocities': final_state['joint_velocities'],
            'ee_position': final_state['ee_position'],
            'ee_rotation': final_state['ee_rotation'],
            'action': action,
            'done': 1  # Done
        })
        
        return trajectory_data

    def collect_sequence(self, cube_position):
        """Collect data for a complete movement sequence"""
        all_trajectory_data = []
        
        # 1. Move to position above cube
        print("Moving to cube position...")
        above_cube = [cube_position[0], cube_position[1] + 0.5, cube_position[2]]
        above_data = self.move_to_position(above_cube, duration=2.0)
        all_trajectory_data.extend(above_data)
        print("Moving to above cube")
        
        down_data = self.move_to_position(cube_position, duration=1.0)
        all_trajectory_data.extend(down_data)
        print("Moving to cube")
        self.robot.WaitDo()
        
        return all_trajectory_data

    def collect_episode(self, episode_idx):
        """Collect data for one episode"""
        print(f"\nCollecting episode {episode_idx}...")
        
        # Move cube to random position and get position
        cube, cube_position = self.place_cube_at_random_position()
        
        # Collect data
        try:
            # Collect movement sequence
            trajectory_data = self.collect_sequence(cube_position)
            
            # Process collected data
            episode_data = {
                'observations': [],
                'actions': [],
                'joint_positions': [],
                'joint_velocities': [],
                'ee_positions': [],
                'ee_rotations': [],
                'dones': []
            }
            
            # Organize data
            for step_data in trajectory_data:
                # Create observation vector
                observation = np.concatenate([
                    step_data['joint_positions'],
                    step_data['joint_velocities'],
                    step_data['ee_position'],
                    step_data['ee_rotation']
                ])
                
                episode_data['observations'].append(observation)
                episode_data['actions'].append(step_data['action'])
                episode_data['joint_positions'].append(step_data['joint_positions'])
                episode_data['joint_velocities'].append(step_data['joint_velocities'])
                episode_data['ee_positions'].append(step_data['ee_position'])
                episode_data['ee_rotations'].append(step_data['ee_rotation'])
                episode_data['dones'].append(step_data['done'])
            
            # Convert to numpy arrays
            for key in episode_data:
                episode_data[key] = np.array(episode_data[key])
                
            print(f"Successfully collected episode {episode_idx} with {len(episode_data['observations'])} steps")
            
            return episode_data
            
        except Exception as e:
            print(f"Error collecting episode {episode_idx}: {e}")
            return None

    def collect_data(self):
        """Collect data for all episodes"""
        all_episodes = []
        
        for episode_idx in tqdm(range(self.num_episodes)):
            episode_data = self.collect_episode(episode_idx)
            if episode_data is not None:
                all_episodes.append(episode_data)
                
        # Save data
        if len(all_episodes) > 0:
            self.save_data(all_episodes)
            print(f"Collected {len(all_episodes)} successful episodes out of {self.num_episodes} attempts")
        else:
            print("No successful episodes were collected")
        
    def save_data(self, episodes):
        """Save collected data"""
        # Create HDF5 file
        file_path = os.path.join(self.data_dir, 'kinova_movement_data.hdf5')
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
    print("Starting Kinova data collection...")
    
    # Create data collector
    collector = KinovaDataCollector(
        data_dir="./data/kinova_data",
        num_episodes=100,  # Reduce number of episodes for testing
        episode_length=100
    )
    
    try:
        # Collect data
        collector.collect_data()
    except KeyboardInterrupt:
        print("\nData collection interrupted by user")
    finally:
        # Close environment
        collector.close()
        
    print("Data collection completed!")