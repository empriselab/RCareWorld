#!/usr/bin/env python3
"""
Convert DiffusionPolicy Zarr 'action' from absolute positions to deltas.

- Copies the entire source .zarr directory to a new destination (default: *_delta.zarr)
- Computes per-step deltas within each episode defined by meta/episode_ends
- Writes deltas back into data/action in the destination
- Optionally preserves the original actions as data/action_abs

Example:
python convert_actions_to_delta.py \
  --src ./data/bathing_dry_upper_20250917_174559.zarr \
  --dst ./data/test_absolute.zarr \
  --keep-absolute
"""

import argparse
import os
import sys
import shutil
from datetime import datetime

import numpy as np
import zarr


def copy_zarr_dir(src: str, dst: str):
    if os.path.exists(dst):
        raise FileExistsError(f"Destination already exists: {dst}")
    print(f"[copy] Copying Zarr dir:\n  src: {src}\n  dst: {dst}")
    shutil.copytree(src, dst)
    print("[copy] Done.")


def ensure_dataset(dst_group, name, like_arr, *, exists_ok=False):
    if name in dst_group:
        if exists_ok:
            return dst_group[name]
        else:
            raise RuntimeError(f"Dataset '{name}' already exists in destination.")
    return dst_group.create_dataset(
        name,
        shape=like_arr.shape,
        dtype=like_arr.dtype,
        chunks=like_arr.chunks or (min(1000, like_arr.shape[0]),) + like_arr.shape[1:],
        compressor=like_arr.compressor,
    )


def compute_deltas_in_episode(abs_slice: np.ndarray) -> np.ndarray:
    """
    abs_slice: (T, D) absolute actions for a single episode
    returns: (T, D) deltas with deltas[0] = 0
    """
    if abs_slice.ndim != 2:
        raise ValueError(f"Expected 2D (T, D), got shape {abs_slice.shape}")
    T = abs_slice.shape[0]
    if T == 0:
        return abs_slice.copy()
    deltas = np.empty_like(abs_slice)
    deltas[0] = 0.0
    if T > 1:
        deltas[1:] = abs_slice[1:] - abs_slice[:-1]
    return deltas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Path to source .zarr directory")
    ap.add_argument("--dst", default=None, help="Destination .zarr (default: add _delta suffix)")
    ap.add_argument("--keep-absolute", action="store_true",
                    help="Store original actions as data/action_abs in the destination")
    args = ap.parse_args()

    src = os.path.abspath(args.src)
    if not os.path.isdir(src):
        sys.exit(f"Not a directory: {src}")

    if args.dst is None:
        base, ext = os.path.splitext(src.rstrip("/"))
        if base.endswith(".zarr"):
            base = base[:-5]
        dst = base + "_delta.zarr"
    else:
        dst = os.path.abspath(args.dst)

    # 1) Copy entire Zarr dir
    copy_zarr_dir(src, dst)

    # 2) Open destination and get arrays
    root = zarr.open(dst, mode="a")
    if "data" not in root:
        sys.exit("Destination missing 'data' group.")
    data = root["data"]

    if "action" not in data:
        sys.exit("Destination missing 'data/action' dataset.")

    action = data["action"]
    print(f"[info] action shape: {action.shape}, dtype: {action.dtype}")

    # Optional: keep original absolute actions
    if args.keep_absolute:
        print("[info] Creating data/action_abs to preserve original actions...")
        action_abs = ensure_dataset(data, "action_abs", action, exists_ok=False)
        # Copy in chunks
        bs = max(1, (10_000_000 // max(1, action.shape[1]) // 4))  # ~10MB chunks
        for start in range(0, action.shape[0], bs):
            end = min(action.shape[0], start + bs)
            action_abs[start:end] = action[start:end]
        action_abs.attrs["note"] = "Original absolute actions copied before delta conversion."
        print("[info] action_abs written.")

    # Episode boundaries
    meta = root.get("meta", None)
    if meta is not None and "episode_ends" in meta:
        episode_ends = np.asarray(meta["episode_ends"][:], dtype=np.int64).tolist()
        print(f"[info] Found episode_ends with {len(episode_ends)} episodes.")
    else:
        episode_ends = [action.shape[0]]
        print("[warn] meta/episode_ends not found; treating entire sequence as a single episode.")

    # 3) Convert per episode
    start = 0
    total = action.shape[0]
    written = 0
    for epi, end in enumerate(episode_ends, start=1):
        if end < start or end > total:
            raise ValueError(f"Invalid episode end index {end} (start={start}, total={total})")

        length = end - start
        if length == 0:
            print(f"[episode {epi}] Empty segment, skipping.")
            start = end
            continue

        # Read episode slice, compute deltas, write back
        abs_slice = action[start:end]  # loads into memory (usually small vs images)
        deltas = compute_deltas_in_episode(abs_slice)
        action[start:end] = deltas
        written += length

        print(f"[episode {epi}] Converted {length} steps "
              f"(frames {start}..{end-1})")

        start = end

    # 4) Mark that actions are now deltas
    action.attrs["format"] = "delta"
    action.attrs["converted_at"] = datetime.now().isoformat(timespec="seconds")
    if args.keep_absolute:
        action.attrs["source_absolute"] = "data/action_abs"
    print(f"[done] Wrote deltas for {written} frames into: {dst}")


if __name__ == "__main__":
    main()
