from pathlib import Path
import argparse, time, os
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
    ap = argparse.ArgumentParser(description="Test LightAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2] /
        "executable" / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="LightTestObject")
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

        light = env.InstanceObject(name=args.name, attr_type=attr.LightAttr)
        print(f"Bound LightAttr to object '{args.name}'")

        # SetColor
        light.SetColor([1.0, 0.8, 0.6])
        step(env, 3)
        print("SetColor executed")

        # SetType (Directional)
        light.SetType(attr.LightType.Directional)
        step(env, 3)
        print("SetType executed (Directional)")

        # SetShadow (Soft)
        light.SetShadow(attr.LightShadow.Soft)
        step(env, 3)
        print("SetShadow executed")

        # SetIntensity
        light.SetIntensity(1.5)
        step(env, 3)
        print("SetIntensity executed")

        # SetType (Point) + SetRange
        light.SetType(attr.LightType.Point)
        step(env, 2)
        light.SetRange(8.0)
        step(env, 3)
        print("SetRange executed (Point)")

        # SetType (Spot) + SetRange + SetSpotAngle
        light.SetType(attr.LightType.Spot)
        step(env, 2)
        light.SetRange(10.0)
        step(env, 2)
        light.SetSpotAngle(45.0)
        step(env, 3)
        print("SetSpotAngle executed (Spot)")

        print("\nAll LightAttr methods invoked successfully")

    finally:
        env.Pend()
        env.close()


if __name__ == "__main__":
    main()
