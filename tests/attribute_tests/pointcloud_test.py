from pathlib import Path
import argparse, time, os
import numpy as np
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld import attributes as attr

def step(env, n=1, delay=0.05):
    for _ in range(n):
        try:
            env.step()
        except Exception:
            pass
        time.sleep(delay)

def main():
    ap = argparse.ArgumentParser(description="Test PointCloudAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="PointCloudTestObject")
    ap.add_argument("--ply", default="", help="Absolute path to a .ply file; if provided, positions/colors are ignored")
    ap.add_argument("--warmup", type=int, default=20)
    args = ap.parse_args()

    player = str(Path(args.player).expanduser().resolve())
    if not Path(player).exists():
        print("Player not found:", player); return
    if os.name != "nt":
        os.chmod(player, os.stat(player).st_mode | 0o111)

    env = RCareWorld(executable_file=player)
    try:
        step(env, args.warmup)

        pc = env.InstanceObject(name=args.name, attr_type=attr.PointCloudAttr)
        print(f"Bound PointCloudAttr to '{args.name}'")

        # ShowPointCloud
        ply_path = args.ply.strip()
        if ply_path:
            ply_abs = str(Path(ply_path).expanduser().resolve())
            if not Path(ply_abs).exists():
                print("PLY not found:", ply_abs); return
            pc.ShowPointCloud(ply_path=ply_abs, positions=None, colors=None, radius=0.01)
        else:
            # generate a small synthetic cloud (sphere)
            n = 2000
            phi = np.random.rand(n).astype(np.float32) * 2.0 * np.pi
            costheta = (np.random.rand(n).astype(np.float32) * 2.0) - 1.0
            theta = np.arccos(costheta).astype(np.float32)
            r = 0.2
            x = (r * np.sin(theta) * np.cos(phi)).reshape(-1, 1)
            y = (r * np.sin(theta) * np.sin(phi)).reshape(-1, 1)
            z = (r * np.cos(theta)).reshape(-1, 1)
            positions = np.concatenate([x, y, z], axis=1).astype(np.float32)

            # colors mapped from normalized coords to [0,1]
            cols = (positions - positions.min(0)) / np.clip((positions.max(0) - positions.min(0)), 1e-6, None)
            colors = cols.astype(np.float32)

            pc.ShowPointCloud(positions=positions, colors=colors, ply_path=None, radius=0.01)
        step(env, 10); print("ShowPointCloud executed")

        # SetRadius
        pc.SetRadius(0.02); step(env, 5); print("SetRadius executed")

        print("\nAll PointCloudAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
