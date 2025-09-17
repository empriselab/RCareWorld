#!/usr/bin/env python3
"""
Generate test data in DiffusionPolicy format with random values but realistic structure.

This script generates zarr datasets that exactly match the format produced by
test_save_data_diffpolicy.py but with random data for testing the training pipeline.

Usage:
    python generate_test_data.py --episodes 10 --steps-per-episode 500
"""

import os
import sys
import argparse
import numpy as np
import zarr
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path to import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def generate_realistic_robot_data(num_steps):
    """Generate realistic robot trajectory data with smooth transitions."""

    # Initialize arrays
    joint_positions = np.zeros((num_steps, 7), dtype=np.float32)
    joint_velocities = np.zeros((num_steps, 7), dtype=np.float32)
    actions = np.zeros((num_steps, 7), dtype=np.float32)
    end_effector_pos = np.zeros((num_steps, 3), dtype=np.float32)
    end_effector_rot = np.zeros((num_steps, 3), dtype=np.float32)
    gripper_state = np.zeros((num_steps, 1), dtype=np.float32)

    # Generate smooth trajectories using sine waves with noise
    t = np.linspace(0, 4*np.pi, num_steps)

    # Joint positions: realistic range [-π, π] with smooth motion
    for j in range(7):
        base = np.sin(t + j * np.pi/7) * 0.5  # Base smooth motion
        noise = np.random.randn(num_steps) * 0.02  # Small noise
        joint_positions[:, j] = np.clip(base + noise, -np.pi, np.pi)

    # Joint velocities: derivative-like with noise
    for j in range(7):
        joint_velocities[1:, j] = np.diff(joint_positions[:, j]) * 50  # Scale to reasonable velocity
        joint_velocities[:, j] = np.clip(joint_velocities[:, j], -2.0, 2.0)

    # Actions: similar to velocities but with control noise
    actions = joint_velocities + np.random.randn(num_steps, 7).astype(np.float32) * 0.1

    # End effector position: workspace bounds roughly [-0.5, 0.5] meters
    end_effector_pos[:, 0] = np.sin(t) * 0.3  # X
    end_effector_pos[:, 1] = np.cos(t) * 0.3 + 0.5  # Y (higher)
    end_effector_pos[:, 2] = np.sin(t * 0.5) * 0.2 + 0.3  # Z

    # End effector rotation: euler angles in radians
    end_effector_rot[:, 0] = np.sin(t * 0.3) * np.pi/4  # Roll
    end_effector_rot[:, 1] = np.cos(t * 0.4) * np.pi/4  # Pitch
    end_effector_rot[:, 2] = np.sin(t * 0.5) * np.pi  # Yaw

    # Gripper state: occasionally open/close
    gripper_changes = np.random.rand(num_steps) > 0.95  # 5% chance to change
    gripper_state[0] = 0.0
    for i in range(1, num_steps):
        if gripper_changes[i]:
            gripper_state[i] = 1.0 - gripper_state[i-1]  # Toggle
        else:
            gripper_state[i] = gripper_state[i-1]  # Keep same state

    return {
        'joint_positions': joint_positions,
        'joint_velocities': joint_velocities,
        'actions': actions,
        'end_effector_pos': end_effector_pos,
        'end_effector_rot': end_effector_rot,
        'gripper_state': gripper_state
    }


def generate_realistic_images(num_steps, width=96, height=96):
    """Generate realistic-looking synthetic images."""

    images = np.zeros((num_steps, height, width, 3), dtype=np.float32)

    for i in range(num_steps):
        # Create a synthetic scene with gradients and shapes

        # Background gradient (simulating table/workspace)
        bg_color = np.array([200, 180, 160], dtype=np.float32)  # Brownish
        for c in range(3):
            images[i, :, :, c] = bg_color[c]

        # Add a circular "object" that moves
        t = i / num_steps * 2 * np.pi
        center_x = int(width/2 + np.sin(t) * width/4)
        center_y = int(height/2 + np.cos(t) * height/4)
        radius = 10

        # Draw circle (object)
        y, x = np.ogrid[:height, :width]
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        object_color = np.array([100, 150, 200], dtype=np.float32)  # Blueish
        for c in range(3):
            images[i, mask, c] = object_color[c]

        # Add robot "gripper" visualization
        gripper_x = int(width/2 + np.sin(t * 1.5) * width/3)
        gripper_y = int(height/2 + np.cos(t * 1.5) * height/3)
        gripper_size = 5

        # Draw gripper as a small square
        y_min = max(0, gripper_y - gripper_size)
        y_max = min(height, gripper_y + gripper_size)
        x_min = max(0, gripper_x - gripper_size)
        x_max = min(width, gripper_x + gripper_size)

        gripper_color = np.array([50, 50, 50], dtype=np.float32)  # Dark gray
        for c in range(3):
            images[i, y_min:y_max, x_min:x_max, c] = gripper_color[c]

        # Add some noise for realism
        noise = np.random.randn(height, width, 3).astype(np.float32) * 5
        images[i] = np.clip(images[i] + noise, 0, 255)

    return images


def create_test_dataset(save_dir="./data", task_name="test_bathing",
                        num_episodes=5, steps_per_episode=300):
    """Create a test dataset with realistic structure but random data."""

    # Create save directory
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    # Create dataset name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_name = f"{task_name}_{timestamp}"
    zarr_path = save_path / f"{dataset_name}.zarr"

    print(f"Creating test dataset: {zarr_path}")

    # Create Zarr store
    store = zarr.open(str(zarr_path), mode='w')
    data_group = store.create_group('data')
    meta_group = store.create_group('meta')

    # Calculate total frames
    total_frames = num_episodes * steps_per_episode

    print(f"Generating {num_episodes} episodes with {steps_per_episode} steps each")
    print(f"Total frames: {total_frames}")

    # Generate all data
    all_images = []
    all_actions = []
    all_states = []
    all_grippers = []
    episode_ends = []

    for ep in range(num_episodes):
        print(f"Generating episode {ep+1}/{num_episodes}...")

        # Generate robot data for this episode
        robot_data = generate_realistic_robot_data(steps_per_episode)

        # Generate images for this episode
        images = generate_realistic_images(steps_per_episode)

        # Combine state data (13 dims: 7 joints + 3 pos + 3 rot)
        states = np.concatenate([
            robot_data['joint_positions'],
            robot_data['end_effector_pos'],
            robot_data['end_effector_rot']
        ], axis=1)

        # Append to lists
        all_images.append(images)
        all_actions.append(robot_data['actions'])
        all_states.append(states)
        all_grippers.append(robot_data['gripper_state'])

        # Calculate episode end index (should be the last frame index + 1)
        episode_end_idx = (ep + 1) * steps_per_episode
        episode_ends.append(episode_end_idx)

    # Concatenate all episodes
    all_images = np.concatenate(all_images, axis=0)
    all_actions = np.concatenate(all_actions, axis=0)
    all_states = np.concatenate(all_states, axis=0)
    all_grippers = np.concatenate(all_grippers, axis=0)
    episode_ends = np.array(episode_ends, dtype=np.int64)

    print("Saving to Zarr format...")

    # Create Zarr arrays with exact format
    # Images: (N, 96, 96, 3) float32 with pixel values [0, 255]
    data_group.create_dataset(
        'img',
        data=all_images,
        dtype=np.float32,
        chunks=(1, 96, 96, 3),
        compression='lz4'
    )

    # Actions: (N, 7) float32
    data_group.create_dataset(
        'action',
        data=all_actions,
        dtype=np.float32,
        chunks=(100, 7),
        compression='lz4'
    )

    # State: (N, 13) float32
    data_group.create_dataset(
        'state',
        data=all_states,
        dtype=np.float32,
        chunks=(100, 13),
        compression='lz4'
    )

    # Gripper: (N, 1) float32
    data_group.create_dataset(
        'gripper',
        data=all_grippers,
        dtype=np.float32,
        chunks=(100, 1),
        compression='lz4'
    )

    # Episode ends
    meta_group.create_dataset(
        'episode_ends',
        data=episode_ends,
        dtype=np.int64,
        compression='lz4'
    )

    print("\n✅ Dataset created successfully!")
    print(f"📁 Location: {zarr_path}")
    print(f"📊 Structure:")
    print(f"   - img: {all_images.shape} (dtype: {all_images.dtype})")
    print(f"   - action: {all_actions.shape} (dtype: {all_actions.dtype})")
    print(f"   - state: {all_states.shape} (dtype: {all_states.dtype})")
    print(f"   - gripper: {all_grippers.shape} (dtype: {all_grippers.dtype})")
    print(f"   - episode_ends: {episode_ends.shape} (dtype: {episode_ends.dtype})")
    print(f"\n📈 Statistics:")
    print(f"   - Episodes: {num_episodes}")
    print(f"   - Steps per episode: {steps_per_episode}")
    print(f"   - Total frames: {total_frames}")
    print(f"   - Image range: [{all_images.min():.1f}, {all_images.max():.1f}]")
    print(f"   - Action range: [{all_actions.min():.3f}, {all_actions.max():.3f}]")
    print(f"   - State range: [{all_states.min():.3f}, {all_states.max():.3f}]")

    return zarr_path


def verify_dataset(zarr_path):
    """Verify the generated dataset matches expected format."""

    print(f"\n🔍 Verifying dataset: {zarr_path}")

    store = zarr.open(str(zarr_path), mode='r')

    # Check structure
    assert 'data' in store, "Missing 'data' group"
    assert 'meta' in store, "Missing 'meta' group"

    data_group = store['data']
    meta_group = store['meta']

    # Check required keys
    required_keys = ['img', 'action', 'state']
    for key in required_keys:
        assert key in data_group, f"Missing required key: {key}"

    # Check data types and shapes
    img = data_group['img']
    assert img.dtype == np.float32, f"Wrong dtype for img: {img.dtype}"
    assert img.ndim == 4, f"Wrong dimensions for img: {img.ndim}"
    assert img.shape[1:] == (96, 96, 3), f"Wrong shape for img: {img.shape}"

    action = data_group['action']
    assert action.dtype == np.float32, f"Wrong dtype for action: {action.dtype}"
    assert action.shape[1] == 7, f"Wrong action dimension: {action.shape[1]}"

    state = data_group['state']
    assert state.dtype == np.float32, f"Wrong dtype for state: {state.dtype}"
    assert state.shape[1] == 13, f"Wrong state dimension: {state.shape[1]}"

    episode_ends = meta_group['episode_ends']
    assert episode_ends.dtype == np.int64, f"Wrong dtype for episode_ends: {episode_ends.dtype}"

    print("✅ All format checks passed!")
    print(f"   - Found {len(data_group.keys())} data arrays")
    print(f"   - Total frames: {len(img)}")
    print(f"   - Episodes: {len(episode_ends)}")

    return True


def main():
    parser = argparse.ArgumentParser(description='Generate test data for DiffusionPolicy training')
    parser.add_argument('--episodes', type=int, default=10,
                      help='Number of episodes to generate (default: 10)')
    parser.add_argument('--steps-per-episode', type=int, default=500,
                      help='Steps per episode (default: 500)')
    parser.add_argument('--task-name', type=str, default='test_bathing',
                      help='Task name for dataset (default: test_bathing)')
    parser.add_argument('--save-dir', type=str, default='./data',
                      help='Directory to save dataset (default: ./data)')
    parser.add_argument('--verify', action='store_true',
                      help='Verify dataset after creation')

    args = parser.parse_args()

    print("=" * 60)
    print("🤖 DiffusionPolicy Test Data Generator")
    print("=" * 60)

    # Generate dataset
    zarr_path = create_test_dataset(
        save_dir=args.save_dir,
        task_name=args.task_name,
        num_episodes=args.episodes,
        steps_per_episode=args.steps_per_episode
    )

    # Optionally verify
    if args.verify:
        verify_dataset(zarr_path)

    print("\n" + "=" * 60)
    print("✨ Done! Dataset ready for DiffusionPolicy training")
    print("=" * 60)


if __name__ == "__main__":
    main()