#!/usr/bin/env python3
import os, sys, time
import numpy as np
import zarr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld

# Path to your saved dataset
ZARR_PATH = "data/bathing_simple_line_20251028_155711.zarr"

ROBOT_ID   = 315893
GRIPPER_ID = 3158930

def load_dataset(zarr_path):
    store = zarr.open(zarr_path, mode="r")
    states = store["data/state"][:]       # (N, 13) float32
    episode_ends = store["meta/episode_ends"][:]
    return states, episode_ends

def episode_ranges(episode_ends):
    prev = -1
    for end in episode_ends:
        yield prev + 1, int(end)
        prev = int(end)

def main():
    states, episode_ends = load_dataset(ZARR_PATH)
    ep_ranges = list(episode_ranges(episode_ends))
    print(f"[Replay] Loaded {len(ep_ranges)} episodes from {ZARR_PATH}")

    env = RCareWorld()
    env.SetTimeStep(0.01)
    robot = env.GetAttr(ROBOT_ID)
    initialize_target = env.GetAttr(5678)
    env.step()
    initialize_position = initialize_target.data["position"]

    try:
        for ep_id, (start, end) in enumerate(ep_ranges):
            print(f"[Replay] Episode {ep_id}: frames {start}–{end}")
            robot.IKTargetDoMove(position=initialize_position, duration=0, speed_based=False)
            robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
            env.step(5)  # settle a few ticks

            for i in range(start, end + 1):
                s = states[i]
                ee_pos = s[7:10].tolist()
                ee_rot = s[10:13].tolist()
                print(ee_pos[0])
                print(ee_rot)

                # Teleport move using EE pose only
                robot.IKTargetDoMove(position=ee_pos, duration=0, speed_based=False)
                robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
                env.step(5)

            print(f"[Replay] Episode {ep_id} complete.\n")

        print("[Replay] All episodes complete.")
    finally:
        env.Pend()

if __name__ == "__main__":
    main()
