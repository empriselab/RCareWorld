#!/usr/bin/env python3
"""
Plot actions (x, y, z) for the FIRST episode only from a DiffusionPolicy-style Zarr dataset.
"""

import argparse
import os
import numpy as np
import zarr
import matplotlib.pyplot as plt


def load_episode_range(root, episode_idx=0):
    meta = root.get("meta", None)
    if meta is None or "episode_ends" not in meta:
        raise SystemExit("No 'meta/episode_ends' found in this dataset")

    ends = np.asarray(meta["episode_ends"][:], dtype=np.int64)
    if episode_idx < 0 or episode_idx >= len(ends):
        raise SystemExit(f"Episode {episode_idx} out of range (total={len(ends)})")

    start = 0 if episode_idx == 0 else ends[episode_idx - 1]
    end = ends[episode_idx]
    return start, end


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zarr", required=True, help="Path to the .zarr dataset")
    ap.add_argument("--dataset", default="action", help="Array name under 'data/' (default: action)")
    args = ap.parse_args()

    root = zarr.open(os.path.abspath(args.zarr), mode="r")
    if "data" not in root or args.dataset not in root["data"]:
        raise SystemExit(f"No 'data/{args.dataset}' found in {args.zarr}")
    actions = root["data"][args.dataset]

    start, end = load_episode_range(root, 0)  # first episode
    A = actions[start:end, :3]  # assume (N,3) for xyz
    T = A.shape[0]

    fmt = str(actions.attrs.get("format", "")) or "unknown"
    print(f"[info] Zarr: {args.zarr}")
    print(f"[info] Using frames [{start}, {end}) for episode 0, total {T} steps")

    x = np.arange(T)

    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    titles = ["Action X", "Action Y"]
    for d in range(2):
        ax = axes[d]
        ax.plot(x, A[:, d], linewidth=1)
        ax.set_ylabel(titles[d])
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("step index (episode 0)")
    fig.suptitle(f"Actions (episode 0, format={fmt})")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


if __name__ == "__main__":
    main()
