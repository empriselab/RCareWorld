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

Data Structure (DiffusionPolicy Compatible):
./data/bathing_task_YYYYMMDD_HHMMSS.zarr/
├── data/
│   ├── action (N, 3) float32           # Robot ee xyz actions
│   ├── img (N, 96, 96, 3) float32      # Camera images [0,255] pixel values
│   ├── state (N, 13) float32           # Robot state (7 joints + 3 pos + 3 rot)
│   └── gripper (N, 1) float32          # Gripper state
└── meta/
    └── episode_ends (E,) int64         # Episode end indices

Where N = total frames across all episodes, E = number of episodes
Note: Images stored as float32 with original [0,255] pixel values, not normalized
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
                 task_name: str = "bathing_task", save_frequency: int = 100,
                 image_width: int = 96, image_height: int = 96):
        """
        Initialize the DiffusionPolicy data saver.

        Args:
            enabled: Whether to enable data saving (default: True)
            save_dir: Base directory for data storage (default: "./data")
            task_name: Name of the task for dataset naming
            save_frequency: Save data every N steps (100=every 1 second at 0.01s timestep, default=100)
            image_width: Width of captured images (default=96 for DiffusionPolicy standard)
            image_height: Height of captured images (default=96 for DiffusionPolicy standard)
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

        # Save frequency control
        self.save_frequency = save_frequency
        self.step_counter = 0  # Internal step counter for frequency control

        # Data buffers for efficient batch writing
        self.frame_buffer = []
        self.buffer_size = 50  # Flush buffer every N frames

        # Camera and robot references
        self.env = None
        self.robot = None
        self.gripper = None
        self.cameras = {}

        # Image settings (configurable, default matches DiffusionPolicy standard)
        self.image_width = image_width
        self.image_height = image_height
        self.image_channels = 3

        # Thread safety
        self.data_lock = threading.Lock()
        self.save_queue = queue.Queue()
        self.save_thread = None

        self.prev_ee_pos = np.zeros(3, dtype=np.float32)  # To compute delta actions

        print(f"[DiffusionPolicy DataSaver] Initialized")
        print(f"[DataSaver] Dataset: {self.dataset_name}")
        print(f"[DataSaver] Save path: {self.zarr_path}")
        print(f"[DataSaver] Save frequency: every {self.save_frequency} step(s)")
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

        # Increment internal step counter
        self.step_counter += 1

        # Check if we should save this step based on frequency
        if self.step_counter % self.save_frequency != 0:
            return

        # Create step data dictionary
        step_data = {
            'step': step_num,
            'timestamp': time.time(),
            'additional': additional_data or {}
        }

        # Capture primary camera image (96x96 for DiffusionPolicy)
        img = None
        primary_camera_id = 91602  # Use first camera as primary
        if primary_camera_id in self.cameras:
            try:
                camera = self.cameras[primary_camera_id]
                camera.GetRGB(width=self.image_width, height=self.image_height)
                self.env.step()  # Need step for image capture

                if camera.data.get("rgb"):
                    # Convert RGB bytes to numpy array
                    rgb_bytes = camera.data["rgb"]

                    # Save to temporary file and read with OpenCV
                    temp_path = f"/tmp/temp_img_{primary_camera_id}.jpg"
                    with open(temp_path, 'wb') as f:
                        f.write(rgb_bytes)

                    # Read image and resize to 96x96
                    img_bgr = cv2.imread(temp_path)
                    if img_bgr is not None:
                        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
                        img = cv2.resize(img, (self.image_width, self.image_height))
                        img = img.astype(np.float32)  # Keep original pixel values [0,255] as float32

                    # show image
                    cv2.imshow("Captured Image", img_bgr)
                    cv2.waitKey(1)
                    # Cleanup temp file
                    try:
                        os.remove(temp_path)
                    except:
                        pass

            except Exception as e:
                print(f"[DataSaver] Warning: Failed to capture image from camera {primary_camera_id}: {e}")



        # Collect robot state (DiffusionPolicy format: flat arrays)
        joint_positions = np.zeros(7, dtype=np.float32)
        end_effector_pos = np.zeros(3, dtype=np.float32)
        end_effector_rot = np.zeros(3, dtype=np.float32)
        gripper_state = np.array([0.0], dtype=np.float32)

        if self.robot:
            try:
                robot_data = self.robot.data

                # Joint positions (7-DOF)
                joints = robot_data.get('joint_positions', [])[:7]
                for i, joint_val in enumerate(joints):
                    if i < 7:
                        joint_positions[i] = joint_val

                # Joint velocities as actions
                joint_vels = robot_data.get('joint_velocities', [])[:7]
                # for i, vel in enumerate(joint_vels):
                #     if i < 7:
                #         action[i] = vel

                # End effector pose
                end_effector_pos = robot_data.get('grasp_point_position', [])
                # print(f"Positions: {positions}")
                end_effector_rot = robot_data.get('grasp_point_rotation', [])
                # print(f"Rotations: {rotations}")

                # elementwise subtraction to get delta
                delta_action = np.zeros(3, dtype=np.float32)
                if self.prev_ee_pos is not None and len(end_effector_pos) == 3:
                    delta_action = np.array(end_effector_pos, dtype=np.float32) - np.array(self.prev_ee_pos, dtype=np.float32)
                self.prev_ee_pos = end_effector_pos

                print(f"Action (Delta EE Position): {delta_action}")

                # print(f"Action (EE Position): {action}")
                
                # Gripper state
                if self.gripper:
                    gripper_data = self.gripper.data
                    gripper_open = gripper_data.get('gripper_open', 0.0)
                    gripper_state = np.array([gripper_open], dtype=np.float32)

            except Exception as e:
                print(f"[DataSaver] Warning: Failed to collect robot state: {e}")

        # Concatenate all state into single array (13 dims: 7 joints + 3 pos + 3 rot)
        state = np.concatenate([joint_positions, end_effector_pos, end_effector_rot], dtype=np.float32)
        # print state shape
        # convert state to array
        state = np.array(state, dtype=np.float32)
        # Combine all data for this step (DiffusionPolicy format)
        frame_data = {
            'step': step_num,
            'img': img,              # (96, 96, 3) float32
            'action': delta_action,  # (3,) float32
            'state': state,          # (13,) float32
            'gripper': gripper_state, # (1,) float32
            'additional': step_data['additional']
        }

        # Add to current episode
        with self.data_lock:
            self.current_episode_data.append(frame_data)
            # Immediately write to zarr arrays
            self._append_frame_to_zarr(frame_data)

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

            # Save data in DiffusionPolicy format
            self.data_group['img'][frame_idx] = frame['img']
            self.data_group['action'][frame_idx] = frame['action']
            self.data_group['state'][frame_idx] = frame['state']
            self.data_group['gripper'][frame_idx] = frame['gripper']

            self.total_frames += 1

        except Exception as e:
            print(f"[DataSaver] Error appending frame to Zarr: {e}")

    def _initialize_zarr_arrays(self, sample_frame: Dict):
        """Initialize Zarr arrays based on first frame structure."""
        try:
            # Estimate total capacity (conservative estimate)
            max_capacity = 50000  # Adjust based on expected dataset size

            # Initialize arrays in DiffusionPolicy format
            # Image array: (N, 96, 96, 3) float32
            img_shape = (max_capacity,) + sample_frame['img'].shape
            self.data_group.create_dataset(
                'img',
                shape=img_shape,
                dtype=sample_frame['img'].dtype,
                chunks=(1,) + sample_frame['img'].shape,
                compression='lz4'
            )

            # Action array: (N, 3) float32
            action_shape = (max_capacity,) + sample_frame['action'].shape
            self.data_group.create_dataset(
                'action',
                shape=action_shape,
                dtype=sample_frame['action'].dtype,
                chunks=(100,) + sample_frame['action'].shape,
                compression='lz4'
            )

            # State array: (N, 13) float32
            state_shape = (max_capacity,) + sample_frame['state'].shape
            self.data_group.create_dataset(
                'state',
                shape=state_shape,
                dtype=sample_frame['state'].dtype,
                chunks=(100,) + sample_frame['state'].shape,
                compression='lz4'
            )

            # Gripper array: (N, 1) float32
            gripper_shape = (max_capacity,) + sample_frame['gripper'].shape
            self.data_group.create_dataset(
                'gripper',
                shape=gripper_shape,
                dtype=sample_frame['gripper'].dtype,
                chunks=(100,) + sample_frame['gripper'].shape,
                compression='lz4'
            )

            print(f"[DataSaver] Zarr arrays initialized with capacity {max_capacity}")
            print(f"[DataSaver] Arrays: img{img_shape[1:]}, action{action_shape[1:]}, state{state_shape[1:]}, gripper{gripper_shape[1:]}")

        except Exception as e:
            print(f"[DataSaver] Error initializing Zarr arrays: {e}")

    def _finalize_current_episode(self):
        """Finalize current episode and update episode_ends."""
        if not self.current_episode_data:
            return

        episode_length = len(self.current_episode_data)
        cumulative_frames = self.total_frames + episode_length

        self.episode_ends.append(cumulative_frames)
        print(f"[DataSaver] Finalized episode {self.current_episode} with {episode_length} frames (cumulative: {cumulative_frames})")

    def finalize(self):
        """Finalize data saving and create final dataset."""
        if not self.enabled:
            return

        print("[DataSaver] Finalizing dataset...")
        with self.data_lock:
            if self.current_episode_data:
                # Data is already written to zarr, just finalize the episode
                self._finalize_current_episode()

        if self.save_thread and self.save_thread.is_alive():
            self.save_queue.put(None)  # Shutdown signal
            self.save_thread.join(timeout=2.0)

        self._finalize_zarr_store()

        print(f"[DataSaver] Dataset finalized: {self.zarr_path}")
        print(f"[DataSaver] Total episodes: {len(self.episode_ends)}")
        print(f"[DataSaver] Total frames: {self.total_frames}")

    def _save_episode_metadata(self):
        """Save episode_ends metadata."""
        if self.episode_ends and 'episode_ends' not in self.meta_group:
            self.meta_group.create_dataset(
                'episode_ends',
                data=np.array(self.episode_ends, dtype=np.int64),
                compression='lz4'
            )
            print(f"[DataSaver] Background saved episode_ends: {self.episode_ends}")

    def _finalize_zarr_store(self):
        """Resize Zarr arrays to actual data size."""
        try:
            # Use the last episode_end as the actual total frames
            actual_total_frames = self.episode_ends[-1] if self.episode_ends else self.total_frames

            if actual_total_frames > 0 and self.data_group is not None:
                keys_to_resize = list(self.data_group.keys())
                for key in keys_to_resize:
                    array = self.data_group[key]
                    if array.shape[0] > actual_total_frames:
                        array.resize(actual_total_frames, *array.shape[1:])
                        print(f"[DataSaver] Resized {key} array to {actual_total_frames} frames")

            # Save final episode_ends
            if self.episode_ends and 'episode_ends' not in self.meta_group:
                self.meta_group.create_dataset(
                    'episode_ends',
                    data=np.array(self.episode_ends, dtype=np.int64),
                    compression='lz4'
                )
                print(f"[DataSaver] Saved episode_ends: {self.episode_ends}")

        except Exception as e:
            print(f"[DataSaver] Error finalizing Zarr store: {e}")


# Global instance and convenience functions
_global_saver = None

def get_data_saver(enabled: bool = True, save_dir: str = "./data",
                   task_name: str = "bathing_task", save_frequency: int = 100,
                   image_width: int = 96, image_height: int = 96) -> DiffusionPolicyDataSaver:
    """Get or create global data saver instance."""
    global _global_saver
    if _global_saver is None:
        _global_saver = DiffusionPolicyDataSaver(enabled=enabled, save_dir=save_dir, task_name=task_name,
                                                 save_frequency=save_frequency, image_width=image_width, image_height=image_height)
    return _global_saver

def init_data_saver(env, robot_id: int = 315893, gripper_id: int = 3158930,
                   enabled: bool = True, task_name: str = "bathing_task", save_frequency: int = 100,
                   image_width: int = 96, image_height: int = 96):
    """Initialize data saver with environment."""
    saver = get_data_saver(enabled=enabled, task_name=task_name, save_frequency=save_frequency,
                          image_width=image_width, image_height=image_height)
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