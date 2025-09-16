"""
Data Saving Module for Diffusion Policy Training - Zarr Format

This module provides a DiffusionPolicy-compatible data saving interface using
Zarr format for efficient storage and loading. The format follows the standard
ReplayBuffer structure with proper episode segmentation.

Key Features:
- Zarr format storage for compatibility with DiffusionPolicy
- Proper episode_ends tracking for episode segmentation
- Multi-camera image observations (IDs: 91601, 91602)
- Complete robot state recording (joints, end-effector, gripper)
- Thread-safe operation with background saving
- Standard ./data/ output directory

Data Structure:
./data/bathing_task_YYYYMMDD_HHMMSS.zarr/
├── data/
│   ├── action (N, Da) float32          # Robot actions
│   ├── obs/
│   │   ├── camera_91601 (N, H, W, 3) uint8    # Camera 1 images
│   │   ├── camera_91602 (N, H, W, 3) uint8    # Camera 2 images
│   │   ├── joint_positions (N, 7) float32      # Robot joint positions
│   │   ├── joint_velocities (N, 7) float32     # Robot joint velocities
│   │   ├── end_effector_pos (N, 3) float32     # End effector position
│   │   ├── end_effector_rot (N, 3) float32     # End effector rotation
│   │   └── gripper_state (N, 1) float32        # Gripper open/close
│   └── ...
└── meta/
    └── episode_ends (E,) int64         # Episode end indices

Where N = total frames across all episodes, E = number of episodes
"""

import os
import json
import time
import numpy as np
import zarr
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import cv2
import threading
import queue
from pathlib import Path
import pyrcareworld.attributes as attr


class DiffusionPolicyDataSaver:
    """
    DiffusionPolicy-compatible data saver using Zarr format.

    This class saves robot demonstration data in the standard format expected
    by DiffusionPolicy training scripts, with proper episode segmentation and
    multi-modal observations.
    """

    def __init__(self, enabled: bool = True, save_dir: str = "./data",
                 task_name: str = "bathing_task"):
        """
        Initialize the DiffusionPolicy data saver.

        Args:
            enabled: Whether to enable data saving (default: True)
            save_dir: Base directory for data storage (default: "./data")
            task_name: Name of the task for dataset naming
        """
        self.enabled = enabled
        if not self.enabled:
            return

        # Create save directory
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Create unique dataset name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dataset_name = f"{task_name}_{timestamp}"
        self.zarr_path = self.save_dir / f"{self.dataset_name}.zarr"

        # Initialize data storage
        self.zarr_store = None
        self.data_group = None
        self.meta_group = None

        # Episode tracking
        self.current_episode_data = []
        self.episode_ends = []
        self.current_episode = 0
        self.total_frames = 0

        # Data buffers for efficient batch writing
        self.frame_buffer = []
        self.buffer_size = 50  # Flush buffer every N frames

        # Camera and robot references
        self.env = None
        self.robot = None
        self.gripper = None
        self.cameras = {}

        # Image settings
        self.image_width = 256
        self.image_height = 256
        self.image_channels = 3

        # Thread safety
        self.data_lock = threading.Lock()
        self.save_queue = queue.Queue()
        self.save_thread = None

        print(f"[DiffusionPolicy DataSaver] Initialized")
        print(f"[DataSaver] Dataset: {self.dataset_name}")
        print(f"[DataSaver] Save path: {self.zarr_path}")
        print(f"[DataSaver] Data saving is {'ENABLED' if self.enabled else 'DISABLED'}")

    def initialize(self, env, robot_id: int = 315893, gripper_id: int = 3158930):
        """
        Initialize with environment and robot components.

        Args:
            env: RCareWorld environment instance
            robot_id: Robot ID for state monitoring
            gripper_id: Gripper ID for state monitoring
        """
        if not self.enabled:
            return

        self.env = env

        # Get robot and gripper references
        try:
            self.robot = env.GetAttr(robot_id)
            self.gripper = env.GetAttr(gripper_id)
            print(f"[DataSaver] Robot (ID: {robot_id}) and gripper (ID: {gripper_id}) connected")
        except Exception as e:
            print(f"[DataSaver] Warning: Could not get robot/gripper: {e}")
            self.robot = None
            self.gripper = None

        # Initialize cameras with proper positioning
        camera_ids = [91601, 91602]
        for cam_id in camera_ids:
            try:
                try:
                    # Try to get existing camera
                    camera = env.GetAttr(cam_id)
                    self.cameras[cam_id] = camera
                    print(f"[DataSaver] Camera {cam_id} found and connected")
                except:
                    # Create camera if it doesn't exist
                    camera = env.InstanceObject(
                        name="Camera",
                        id=cam_id,
                        attr_type=attr.CameraAttr
                    )

                    # Set camera positions for optimal viewpoints
                    if cam_id == 91601:
                        # Front-top view
                        camera.SetTransform(
                            position=[0, 1.2, -1.0],
                            rotation=[45, 0, 0]
                        )
                    elif cam_id == 91602:
                        # Side view
                        camera.SetTransform(
                            position=[1.0, 0.8, 0.2],
                            rotation=[30, -60, 0]
                        )

                    self.cameras[cam_id] = camera
                    print(f"[DataSaver] Camera {cam_id} created and positioned")

            except Exception as e:
                print(f"[DataSaver] Warning: Could not initialize camera {cam_id}: {e}")

        # Initialize Zarr store
        self._initialize_zarr_store()

        # Start background saving thread
        self.save_thread = threading.Thread(target=self._background_saver, daemon=True)
        self.save_thread.start()

    def _initialize_zarr_store(self):
        """Initialize Zarr store with proper structure."""
        try:
            # Create Zarr store
            self.zarr_store = zarr.open(str(self.zarr_path), mode='w')

            # Create main groups
            self.data_group = self.zarr_store.create_group('data')
            self.meta_group = self.zarr_store.create_group('meta')

            print(f"[DataSaver] Zarr store initialized at {self.zarr_path}")

        except Exception as e:
            print(f"[DataSaver] Error initializing Zarr store: {e}")
            self.enabled = False

    def start_new_episode(self):
        """Start a new episode and save previous episode data."""
        if not self.enabled:
            return

        with self.data_lock:
            # Finalize current episode if it has data
            if self.current_episode_data:
                self._finalize_current_episode()

            # Reset for new episode
            self.current_episode += 1
            self.current_episode_data = []
            print(f"[DataSaver] Started episode {self.current_episode}")

    def save_step(self, step_num: int, additional_data: Dict[str, Any] = None):
        """
        Save current step data in DiffusionPolicy format.

        Args:
            step_num: Current step number
            additional_data: Optional additional data to include
        """
        if not self.enabled:
            return

        # Create step data dictionary
        step_data = {
            'step': step_num,
            'timestamp': time.time(),
            'additional': additional_data or {}
        }

        # Capture camera images
        images = {}
        for cam_id, camera in self.cameras.items():
            try:
                # Capture RGB image with specified resolution
                camera.GetRGB(width=self.image_width, height=self.image_height)
                self.env.step()  # Need step for image capture

                if camera.data.get("rgb"):
                    # Convert RGB bytes to numpy array
                    rgb_bytes = camera.data["rgb"]

                    # Save to temporary file and read with OpenCV
                    temp_path = f"/tmp/temp_img_{cam_id}.jpg"
                    with open(temp_path, 'wb') as f:
                        f.write(rgb_bytes)

                    # Read image and resize if necessary
                    img = cv2.imread(temp_path)
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
                        img = cv2.resize(img, (self.image_width, self.image_height))
                        images[f'camera_{cam_id}'] = img.astype(np.uint8)

                    # Cleanup temp file
                    try:
                        os.remove(temp_path)
                    except:
                        pass

            except Exception as e:
                print(f"[DataSaver] Warning: Failed to capture image from camera {cam_id}: {e}")

        # Collect robot state
        robot_state = {}
        if self.robot:
            try:
                robot_data = self.robot.data

                # Joint states (assuming 7-DOF robot)
                joint_positions = robot_data.get('joint_positions', [])[:7]
                joint_velocities = robot_data.get('joint_velocities', [])[:7]

                # Pad to 7 DOF if necessary
                while len(joint_positions) < 7:
                    joint_positions.append(0.0)
                while len(joint_velocities) < 7:
                    joint_velocities.append(0.0)

                robot_state['joint_positions'] = np.array(joint_positions, dtype=np.float32)
                robot_state['joint_velocities'] = np.array(joint_velocities, dtype=np.float32)

                # End effector pose
                positions = robot_data.get('positions', [])
                rotations = robot_data.get('rotations', [])

                if len(positions) > 6:
                    robot_state['end_effector_pos'] = np.array(positions[6][:3], dtype=np.float32)
                else:
                    robot_state['end_effector_pos'] = np.zeros(3, dtype=np.float32)

                if len(rotations) > 6:
                    robot_state['end_effector_rot'] = np.array(rotations[6][:3], dtype=np.float32)
                else:
                    robot_state['end_effector_rot'] = np.zeros(3, dtype=np.float32)

                # Gripper state
                if self.gripper:
                    gripper_data = self.gripper.data
                    gripper_open = gripper_data.get('gripper_open', 0.0)
                    robot_state['gripper_state'] = np.array([gripper_open], dtype=np.float32)
                else:
                    robot_state['gripper_state'] = np.array([0.0], dtype=np.float32)

            except Exception as e:
                print(f"[DataSaver] Warning: Failed to collect robot state: {e}")
                # Set default values
                robot_state = {
                    'joint_positions': np.zeros(7, dtype=np.float32),
                    'joint_velocities': np.zeros(7, dtype=np.float32),
                    'end_effector_pos': np.zeros(3, dtype=np.float32),
                    'end_effector_rot': np.zeros(3, dtype=np.float32),
                    'gripper_state': np.array([0.0], dtype=np.float32)
                }

        # Create action (for now, use joint velocities as proxy action)
        # In actual implementation, this should be the commanded action
        action = robot_state.get('joint_velocities', np.zeros(7, dtype=np.float32))

        # Combine all data for this step
        frame_data = {
            'step': step_num,
            'images': images,
            'robot_state': robot_state,
            'action': action,
            'additional': step_data['additional']
        }

        # Add to current episode
        with self.data_lock:
            self.current_episode_data.append(frame_data)

        # Add to buffer for batch saving
        self.frame_buffer.append(frame_data)
        if len(self.frame_buffer) >= self.buffer_size:
            self._flush_buffer()

    def _flush_buffer(self):
        """Flush frame buffer to background saving queue."""
        if self.frame_buffer:
            # Copy buffer and clear
            buffer_copy = self.frame_buffer.copy()
            self.frame_buffer.clear()

            # Queue for background saving
            self.save_queue.put(('frames', buffer_copy))

    def _background_saver(self):
        """Background thread for saving data to Zarr."""
        while True:
            try:
                item = self.save_queue.get(timeout=1.0)
                if item is None:  # Shutdown signal
                    break

                item_type, data = item
                if item_type == 'frames':
                    self._save_frames_to_zarr(data)
                elif item_type == 'finalize':
                    self._save_episode_metadata()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[DataSaver] Background saving error: {e}")

    def _save_frames_to_zarr(self, frames: List[Dict]):
        """Save frames to Zarr arrays."""
        if not frames or not self.enabled:
            return

        try:
            for frame in frames:
                self._append_frame_to_zarr(frame)
                self.total_frames += 1

        except Exception as e:
            print(f"[DataSaver] Error saving frames to Zarr: {e}")

    def _append_frame_to_zarr(self, frame: Dict):
        """Append a single frame to Zarr arrays."""
        try:
            # Initialize arrays if this is the first frame
            if self.total_frames == 0:
                self._initialize_zarr_arrays(frame)

            frame_idx = self.total_frames

            # Save images
            for img_key, img_data in frame['images'].items():
                if img_key in self.data_group:
                    self.data_group[img_key][frame_idx] = img_data

            # Save robot state
            for state_key, state_data in frame['robot_state'].items():
                if state_key in self.data_group:
                    self.data_group[state_key][frame_idx] = state_data

            # Save action
            self.data_group['action'][frame_idx] = frame['action']

        except Exception as e:
            print(f"[DataSaver] Error appending frame to Zarr: {e}")

    def _initialize_zarr_arrays(self, sample_frame: Dict):
        """Initialize Zarr arrays based on first frame structure."""
        try:
            # Estimate total capacity (conservative estimate)
            max_capacity = 50000  # Adjust based on expected dataset size

            # Initialize image arrays
            for img_key, img_data in sample_frame['images'].items():
                shape = (max_capacity,) + img_data.shape
                self.data_group.create_dataset(
                    img_key,
                    shape=shape,
                    dtype=img_data.dtype,
                    chunks=(1,) + img_data.shape,
                    compression='lz4'
                )

            # Initialize robot state arrays
            for state_key, state_data in sample_frame['robot_state'].items():
                shape = (max_capacity,) + state_data.shape
                self.data_group.create_dataset(
                    state_key,
                    shape=shape,
                    dtype=state_data.dtype,
                    chunks=(100,) + state_data.shape
                )

            # Initialize action array
            action_shape = (max_capacity,) + sample_frame['action'].shape
            self.data_group.create_dataset(
                'action',
                shape=action_shape,
                dtype=sample_frame['action'].dtype,
                chunks=(100,) + sample_frame['action'].shape
            )

            print(f"[DataSaver] Zarr arrays initialized with capacity {max_capacity}")

        except Exception as e:
            print(f"[DataSaver] Error initializing Zarr arrays: {e}")

    def _finalize_current_episode(self):
        """Finalize current episode and update episode_ends."""
        if not self.current_episode_data:
            return

        episode_length = len(self.current_episode_data)
        episode_end_idx = self.total_frames + episode_length - 1

        self.episode_ends.append(episode_end_idx)
        print(f"[DataSaver] Finalized episode {self.current_episode} with {episode_length} frames (end_idx: {episode_end_idx})")

    def finalize(self):
        """Finalize data saving and create final dataset."""
        if not self.enabled:
            return

        print("[DataSaver] Finalizing dataset...")

        # Flush remaining buffer
        if self.frame_buffer:
            self._flush_buffer()

        # Finalize current episode
        with self.data_lock:
            if self.current_episode_data:
                self._finalize_current_episode()

        # Signal background thread to save final metadata
        self.save_queue.put(('finalize', None))

        # Wait for background thread to finish
        if self.save_thread and self.save_thread.is_alive():
            self.save_queue.put(None)  # Shutdown signal
            self.save_thread.join(timeout=5.0)

        # Resize arrays to actual data size and save episode_ends
        self._finalize_zarr_store()

        print(f"[DataSaver] Dataset finalized: {self.zarr_path}")
        print(f"[DataSaver] Total episodes: {len(self.episode_ends)}")
        print(f"[DataSaver] Total frames: {self.total_frames}")

    def _save_episode_metadata(self):
        """Save episode_ends metadata."""
        if self.episode_ends:
            self.meta_group.create_dataset(
                'episode_ends',
                data=np.array(self.episode_ends, dtype=np.int64),
                compression='lz4'
            )

    def _finalize_zarr_store(self):
        """Resize Zarr arrays to actual data size."""
        try:
            if self.total_frames > 0 and self.data_group is not None:
                # Resize all arrays to actual size
                for key in self.data_group.keys():
                    array = self.data_group[key]
                    if len(array) > self.total_frames:
                        # Create new array with correct size
                        new_array = self.data_group.create_dataset(
                            f"{key}_resized",
                            data=array[:self.total_frames],
                            compression='lz4'
                        )
                        # Replace old array
                        del self.data_group[key]
                        self.data_group[key] = new_array

            # Save final episode_ends
            if self.episode_ends:
                self.meta_group.create_dataset(
                    'episode_ends',
                    data=np.array(self.episode_ends, dtype=np.int64),
                    compression='lz4'
                )

        except Exception as e:
            print(f"[DataSaver] Error finalizing Zarr store: {e}")


# Global instance and convenience functions
_global_saver = None

def get_data_saver(enabled: bool = True, save_dir: str = "./data",
                   task_name: str = "bathing_task") -> DiffusionPolicyDataSaver:
    """Get or create global data saver instance."""
    global _global_saver
    if _global_saver is None:
        _global_saver = DiffusionPolicyDataSaver(enabled=enabled, save_dir=save_dir, task_name=task_name)
    return _global_saver

def init_data_saver(env, robot_id: int = 315893, gripper_id: int = 3158930,
                   enabled: bool = True, task_name: str = "bathing_task"):
    """Initialize data saver with environment."""
    saver = get_data_saver(enabled=enabled, task_name=task_name)
    saver.initialize(env, robot_id, gripper_id)
    return saver

def save_step_data(step_num: int, additional_data: Dict = None):
    """Save current step data."""
    saver = get_data_saver()
    saver.save_step(step_num, additional_data)

def start_new_episode():
    """Start a new episode."""
    saver = get_data_saver()
    saver.start_new_episode()

def finalize_data_saving():
    """Finalize and save all data."""
    saver = get_data_saver()
    saver.finalize()