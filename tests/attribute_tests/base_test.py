from pathlib import Path
import argparse, time, os
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
    ap = argparse.ArgumentParser(description="Test all BaseAttr methods")
    default_player = (
    Path(__file__).resolve().parents[2]
    / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
    / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )


    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="BaseTestObject")
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
        obj = env.InstanceObject(name=args.name, attr_type=attr.BaseAttr)
        print(f"Bound BaseAttr to object '{args.name}'")

        # transform functions
        obj.SetPosition([0, 1, 0])
        obj.SetRotation([0, 45, 0])
        obj.SetScale([1, 2, 1])
        step(env, 3)
        print("Basic transforms executed")

        # translate and rotate
        obj.Translate([0, 0, 1])
        obj.Rotate([0, 45, 0])
        step(env, 3)
        print("Translate & Rotate executed")

        # LookAt()
        obj.LookAt([0, 0, 0])
        step(env, 3)
        print("LookAt executed")

        # SetActive()
        obj.SetActive(False)
        step(env, 3)
        obj.SetActive(True)
        print("SetActive toggled")

        # Layering
        obj.SetLayer(0)
        print("SetLayer(0) executed")

        # Tweening
        obj.DoMove([2, 1, 0], 1.0)
        obj.DoRotate([0, 180, 0], 1.0)
        step(env, 10)
        obj.DoComplete()
        print("DoMove / DoRotate / DoComplete tested")

        # Copy & Destroy
        new_id = 9999
        new_obj = obj.Copy(new_id)
        print(f"Copy created new object with id {new_id}")
        step(env, 3)
        new_obj.Destroy()
        print("Destroy executed")

        # Local/world point conversion
        obj.GetLocalPointFromWorld([0.5, 0.5, 0.5])
        obj.GetWorldPointFromLocal([1.0, 0.0, 0.0])
        step(env, 3)
        print("Point conversions executed")

        # DoKill()
        obj.DoKill()
        print("DoKill executed")

        print("\nAll BaseAttr methods invoked successfully")
    finally:
        env.Pend()
        env.close()


if __name__ == "__main__":
    main()
