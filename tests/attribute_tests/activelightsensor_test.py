from pathlib import Path
import argparse, os, time
import numpy as np
import cv2

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld import attributes as attr

def main():
    ap = argparse.ArgumentParser(description="Test ActiveLightSensorAttr end-to-end")
    default_player = (
        Path(__file__).resolve().parents[2] /
        "executable" / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player),
                    help="Path to Unity player (Attribute_Tests.x86_64 or .exe)")
    ap.add_argument("--name", default="ActiveLightSensor",
                    help="Scene object name (default: ActiveLightSensor)")
    ap.add_argument("--warmup", type=int, default=20)
    args = ap.parse_args()

    player = str(Path(args.player).expanduser().resolve())

    env = RCareWorld(executable_file=player)
    try:
        for _ in range(args.warmup):
            try: env.step()
            except Exception: pass
            time.sleep(0.05)

        # Bind the attribute
        sensor = env.InstanceObject(name=args.name, attr_type=attr.ActiveLightSensorAttr)
        print(">>> Bound ActiveLightSensorAttr")

        # Intrinsic matrices (fake identity just for test)
        main_intr = np.array([[600,0,320],[0,600,240],[0,0,1]], dtype=np.float32)
        ir_intr   = np.array([[600,0,320],[0,600,240],[0,0,1]], dtype=np.float32)

        # Request an active depth frame
        print(">>> Requesting active depth...")
        sensor.GetActiveDepth(main_intr, ir_intr)

        # Stepto receive data
        for _ in range(10):
            try: env.step()
            except Exception: pass
            time.sleep(0.05)

        # Inspect received data
        data_keys = list(sensor.data.keys())
        print("Data keys received:", data_keys)
        if "active_depth" in sensor.data:
            depth = sensor.data["active_depth"]
            print("Depth shape:", depth.shape, "dtype:", depth.dtype)
            np.save("active_depth.npy", depth)
            cv2.imwrite("active_depth_vis.png", (depth/np.nanmax(depth)*255).astype(np.uint8))
            print("Saved active_depth_vis.png")
        else:
            print("No 'active_depth' field found. "
                  "Ensure your Unity scene sends ir_left/ir_right images.")

        print("ActiveLightSensorAttr test complete.")
    finally:
        env.Pend()
        env.close()

if __name__ == "__main__":
    main()
