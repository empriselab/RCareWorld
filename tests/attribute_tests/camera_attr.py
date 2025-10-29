from pathlib import Path
import argparse, time, os
import numpy as np
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld import attributes as attr


def step(env, n=1, delay=0.05):
    """Try stepping forward a few frames."""
    for _ in range(n):
        try:
            env.step()
        except Exception:
            pass
        time.sleep(delay)


def main():
    ap = argparse.ArgumentParser(description="Test all CameraAttr methods")
    default_player = (
    Path(__file__).resolve().parents[2]
    / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
    / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="CameraTestObject")
    ap.add_argument("--warmup", type=int, default=20)
    args = ap.parse_args()

    player = str(Path(args.player).expanduser().resolve())
    if not Path(player).exists():
        print("Player not found:", player)
        return
    if os.name != "nt":
        os.chmod(player, os.stat(player).st_mode | 0o111)

    env = RCareWorld(executable_file=player)
    try:
        step(env, args.warmup)

        cam = env.InstanceObject(name=args.name, attr_type=attr.CameraAttr)
        print(f"Bound CameraAttr to object '{args.name}'")

        # AlignView()
        cam.AlignView()
        step(env, 3)
        print("AlignView executed")

        # GetRGB()
        cam.GetRGB(width=256, height=256, fov=60.0)
        step(env, 3)
        print("GetRGB executed")

        # GetNormal()
        cam.GetNormal(width=256, height=256, fov=60.0)
        step(env, 3)
        print("GetNormal executed")

        # GetDepth()
        cam.GetDepth(zero_dis=0.1, one_dis=5.0, width=256, height=256)
        step(env, 3)
        print("GetDepth executed")

        # GetDepth16Bit()
        cam.GetDepth16Bit(zero_dis=0.1, one_dis=5.0, width=256, height=256)
        step(env, 3)
        print("GetDepth16Bit executed")

        # GetDepthEXR()
        cam.GetDepthEXR(width=256, height=256, fov=60.0)
        step(env, 3)
        print("GetDepthEXR executed")

        # GetID()
        cam.GetID(width=256, height=256, fov=60.0)
        step(env, 3)
        print("GetID executed")

        # GetAmodalMask()
        cam.GetAmodalMask(target_id=1, width=256, height=256, fov=60.0)
        step(env, 3)
        print("GetAmodalMask executed")

        # StartHeatMapRecord() / EndHeatMapRecord()
        cam.StartHeatMapRecord(targets_id=[1])
        step(env, 3)
        print("StartHeatMapRecord executed")

        cam.EndHeatMapRecord()
        step(env, 3)
        print("EndHeatMapRecord executed")

        # GetHeatMap()
        cam.GetHeatMap(width=256, height=256, radius=30)
        step(env, 3)
        print("GetHeatMap executed")

        # GetD2DBBox() / Get3DBBox()
        cam.Get2DBBox(width=256, height=256, fov=60.0)
        step(env, 3)
        print("Get2DBBox executed")

        cam.Get3DBBox()
        step(env, 3)
        print("Get3DBBox executed")

        print("\nAll CameraAttr methods invoked successfully")

    finally:
        env.Pend()
        env.close()


if __name__ == "__main__":
    main()
