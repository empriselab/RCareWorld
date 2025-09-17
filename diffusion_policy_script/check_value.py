#!/usr/bin/env python3
"""
Summarize delta robot actions stored in a DiffusionPolicy Zarr dataset.

It prints:
- number of frames and action dimensionality
- per-dimension mean, min, and max of data/action
- overall (scalar) min and max across all dimensions

Assumes data/action already contains DELTAS.
If your file still has absolute actions, run your conversion first.

Usage:
  python check_value.py --zarr ./data/test_absolute.zarr
"""

import argparse
import os
import sys
import numpy as np
import zarr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zarr", required=True, help="Path to the .zarr directory")
    ap.add_argument("--dataset", default="action", help="Dataset path under 'data/' (default: action)")
    ap.add_argument("--chunk-rows", type=int, default=131072,
                    help="How many rows to process per chunk (default: 131072)")
    args = ap.parse_args()

    zarr_path = os.path.abspath(args.zarr)
    if not os.path.isdir(zarr_path):
        sys.exit(f"Not a directory: {zarr_path}")

    root = zarr.open(zarr_path, mode="r")
    if "data" not in root:
        sys.exit("No 'data' group found in the Zarr store.")
    data = root["data"]

    if args.dataset not in data:
        sys.exit(f"'data/{args.dataset}' not found in the Zarr store.")
    actions = data[args.dataset]

    if actions.ndim != 2:
        sys.exit(f"'data/{args.dataset}' must be 2D (N, D). Got shape {actions.shape}.")

    N, D = actions.shape
    fmt = actions.attrs.get("format", None)

    print(f"Zarr: {zarr_path}")
    print(f"Dataset: data/{args.dataset}")
    print(f"Shape: (N={N}, D={D}), dtype={actions.dtype}")
    if fmt is not None:
        print(f"format attr: {fmt!r}")
    if fmt is None or str(fmt).lower() != "delta":
        print("⚠️  Warning: 'format' attr is not 'delta'. "
              "Make sure this dataset already contains per-step deltas.")

    # Streaming stats
    sum_vec = np.zeros(D, dtype=np.float64)
    min_vec = np.full(D, np.inf, dtype=np.float64)
    max_vec = np.full(D, -np.inf, dtype=np.float64)

    bs = max(1, int(args.chunk_rows))
    total_rows = 0

    for start in range(0, N, bs):
        end = min(N, start + bs)
        chunk = actions[start:end]  # (M, D)
        # Sum
        sum_vec += chunk.sum(axis=0, dtype=np.float64)
        # Min/Max per dim
        min_vec = np.minimum(min_vec, chunk.min(axis=0))
        max_vec = np.maximum(max_vec, chunk.max(axis=0))
        total_rows += (end - start)

    assert total_rows == N, "Processed row count mismatch."

    mean_vec = sum_vec / float(N)
    overall_min = float(min_vec.min())
    overall_max = float(max_vec.max())

    # Pretty print
    np.set_printoptions(precision=6, suppress=True)
    print("\nPer-dimension statistics:")
    print(f"  mean: {mean_vec}")
    print(f"  min : {min_vec}")
    print(f"  max : {max_vec}")

    print("\nOverall (across all dimensions):")
    print(f"  global min: {overall_min}")
    print(f"  global max: {overall_max}")

if __name__ == "__main__":
    main()
