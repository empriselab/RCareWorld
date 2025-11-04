# save_data_diffusion.py
"""
DiffusionPolicy-compatible Zarr saver (NO THREADS, NO try/except)

Layout:
<dataset>.zarr/
  data/
    action  (N, 3) float32
    img     (N, 96, 96, 3) float32
    state   (N, 13) float32
    gripper (N, 1) float32
  meta/
    episode_ends (E,) int64
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
import zarr
import pyrcareworld.attributes as attr


class DiffusionPolicyDataSaver:
    def __init__(
        self,
        enabled: bool = True,
        save_dir: str = "./data",
        task_name: str = "bathing_task",
        save_frequency: int = 100,
        image_width: int = 96,
        image_height: int = 96,
    ):
        self.enabled = enabled
        if not self.enabled:
            return

        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.dataset_name = f"{task_name}_{ts}"
        self.zarr_path = self.save_dir / f"{self.dataset_name}.zarr"

        self.env = None
        self.robot = None
        self.gripper = None
        self.cameras: Dict[int, Any] = {}

        self.current_episode_has_data = False
        self.episode_ends: List[int] = []
        self.total_frames = 0
        self.step_counter = 0
        self.save_frequency = save_frequency

        self.image_width = image_width
        self.image_height = image_height

        self.z = None
        self.data_group = None
        self.meta_group = None
        self._arrays_initialized = False

        print(f"[DataSaver] Initialized")
        print(f"[DataSaver] Dataset: {self.dataset_name}")
        print(f"[DataSaver] Save path: {self.zarr_path}")
        print(f"[DataSaver] Save frequency: every {self.save_frequency} step(s)")

    # ---------- public API ----------

    def initialize(self, env, robot_id: int = 315893, gripper_id: int = 3158930):
        if not self.enabled:
            return

        self.env = env
        self.robot = env.GetAttr(robot_id)
        self.gripper = env.GetAttr(gripper_id)

        # Connect or create cameras; no try/except — failures will raise.
        for cam_id in [91601, 91602]:
            cam = env.GetAttr(cam_id)
            self.cameras[cam_id] = cam

        self._open_store()

    def start_new_episode(self):
        if not self.enabled:
            return
        if self.current_episode_has_data:
            self._mark_episode_end()
        self.current_episode_has_data = False
        print(f"[DataSaver] Start new episode #{len(self.episode_ends) + 1}")

    def save_step(self, step_num: int, additional_data: Optional[Dict[str, Any]] = None):
        """Call once per sim step. Writes synchronously."""
        if not self.enabled:
            return

        self.step_counter += 1
        if (self.step_counter % self.save_frequency) != 0:
            return

        # image from primary camera
        img = self._capture_rgb(91602)
        if img is None:
            print("[DataSaver] WARN: image capture returned None; frame skipped")
            return

        # robot state
        joint_positions = np.zeros(7, dtype=np.float32)
        ee_pos = np.zeros(3, dtype=np.float32)
        ee_rot = np.zeros(3, dtype=np.float32)
        grip = np.array([0.0], dtype=np.float32)

        rd = self.robot.data
        jp = rd.get("joint_positions", [])[:7]
        for i in range(min(7, len(jp))):
            joint_positions[i] = float(jp[i])

        p = rd.get("grasp_point_position", [])
        r = rd.get("grasp_point_rotation", [])
        if len(p) == 3:
            ee_pos = np.array(p, dtype=np.float32)
        if len(r) == 3:
            ee_rot = np.array(r, dtype=np.float32)

        gd = self.gripper.data
        grip = np.array([float(gd.get("gripper_open", 0.0))], dtype=np.float32)

        state = np.concatenate([joint_positions, ee_pos, ee_rot]).astype(np.float32)
        action = ee_pos.astype(np.float32)  # absolute EE position

        if not self._arrays_initialized:
            self._init_arrays(sample_img=img, sample_action=action, sample_state=state, sample_gripper=grip)

        idx = self.total_frames
        self.data_group["img"][idx] = img
        self.data_group["action"][idx] = action
        self.data_group["state"][idx] = state
        self.data_group["gripper"][idx] = grip

        self.total_frames += 1
        self.current_episode_has_data = True

    def finalize(self):
        if not self.enabled:
            return
        print("[DataSaver] Finalizing...")
        if self.current_episode_has_data:
            self._mark_episode_end()
        self._write_episode_ends()
        self._shrink_to_fit()
        print(f"[DataSaver] Dataset finalized: {self.zarr_path}")
        print(f"[DataSaver] Episodes: {len(self.episode_ends)} | Frames: {self.total_frames}")

    # ---------- internals ----------

    def _open_store(self):
        self.z = zarr.open(str(self.zarr_path), mode="w")
        self.data_group = self.z.create_group("data")
        self.meta_group = self.z.create_group("meta")
        print(f"[DataSaver] Zarr store ready at {self.zarr_path}")

    def _init_arrays(self, sample_img: np.ndarray, sample_action: np.ndarray,
                     sample_state: np.ndarray, sample_gripper: np.ndarray):
        max_capacity = 50000  # conservative cap; will shrink at finalize

        self.data_group.create_dataset(
            "img",
            shape=(max_capacity,) + sample_img.shape,
            dtype=sample_img.dtype,
            chunks=(1,) + sample_img.shape,
            compression="lz4",
        )
        self.data_group.create_dataset(
            "action",
            shape=(max_capacity,) + sample_action.shape,
            dtype=sample_action.dtype,
            chunks=(100,) + sample_action.shape,
            compression="lz4",
        )
        self.data_group.create_dataset(
            "state",
            shape=(max_capacity,) + sample_state.shape,
            dtype=sample_state.dtype,
            chunks=(100,) + sample_state.shape,
            compression="lz4",
        )
        self.data_group.create_dataset(
            "gripper",
            shape=(max_capacity,) + sample_gripper.shape,
            dtype=sample_gripper.dtype,
            chunks=(100,) + sample_gripper.shape,
            compression="lz4",
        )
        self._arrays_initialized = True
        print(f"[DataSaver] Arrays initialized (capacity={max_capacity}) "
              f"img{sample_img.shape}, action{sample_action.shape}, state{sample_state.shape}, gripper{sample_gripper.shape}")

    def _capture_rgb(self, cam_id: int) -> Optional[np.ndarray]:
        cam = self.cameras.get(cam_id)
        if cam is None:
            return None

        cam.GetRGB(width=self.image_width, height=self.image_height)
        if self.env:
            self.env.step()

        rgb_bytes = cam.data.get("rgb", None)
        if not rgb_bytes:
            return None

        tmp = f"/tmp/dp_img_{cam_id}.jpg"
        with open(tmp, "wb") as f:
            f.write(rgb_bytes)
        bgr = cv2.imread(tmp)
        os.remove(tmp)

        if bgr is None:
            return None
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        if (rgb.shape[1], rgb.shape[0]) != (self.image_width, self.image_height):
            rgb = cv2.resize(rgb, (self.image_width, self.image_height))
        return rgb.astype(np.float32)  # keep [0,255] in float32

    def _mark_episode_end(self):
        self.episode_ends.append(self.total_frames)
        print(f"[DataSaver] Episode ended at frame {self.total_frames}")

    def _write_episode_ends(self):
        if "episode_ends" in self.meta_group:
            del self.meta_group["episode_ends"]
        self.meta_group.create_dataset(
            "episode_ends",
            data=np.asarray(self.episode_ends, dtype=np.int64),
            compression="lz4",
        )
        print(f"[DataSaver] Saved episode_ends: {self.episode_ends}")

    def _shrink_to_fit(self):
        actual = self.total_frames
        if actual <= 0:
            return
        for key in ["img", "action", "state", "gripper"]:
            arr = self.data_group[key]
            if arr.shape[0] > actual:
                arr.resize(actual, *arr.shape[1:])
                print(f"[DataSaver] Resized {key} -> {actual}")


# -------- global convenience (same import surface) --------

_global_saver: Optional[DiffusionPolicyDataSaver] = None

def get_data_saver(
    enabled: bool = True,
    save_dir: str = "./data",
    task_name: str = "bathing_task",
    save_frequency: int = 100,
    image_width: int = 96,
    image_height: int = 96,
) -> DiffusionPolicyDataSaver:
    global _global_saver
    if _global_saver is None:
        _global_saver = DiffusionPolicyDataSaver(
            enabled=enabled,
            save_dir=save_dir,
            task_name=task_name,
            save_frequency=save_frequency,
            image_width=image_width,
            image_height=image_height,
        )
    return _global_saver

def init_data_saver(
    env,
    robot_id: int = 315893,
    gripper_id: int = 3158930,
    enabled: bool = True,
    task_name: str = "bathing_task",
    save_frequency: int = 100,
    image_width: int = 96,
    image_height: int = 96,
):
    saver = get_data_saver(
        enabled=enabled,
        task_name=task_name,
        save_frequency=save_frequency,
        image_width=image_width,
        image_height=image_height,
    )
    saver.initialize(env, robot_id, gripper_id)
    return saver

def save_step_data(step_num: int, additional_data: Optional[Dict[str, Any]] = None):
    saver = get_data_saver()
    saver.save_step(step_num, additional_data)

def start_new_episode():
    saver = get_data_saver()
    saver.start_new_episode()

def finalize_data_saving():
    saver = get_data_saver()
    saver.finalize()
