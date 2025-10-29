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
    ap = argparse.ArgumentParser(description="Test HumanbodyAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="HumanBodyTestObject")
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

        hb = env.InstanceObject(name=args.name, attr_type=attr.HumanbodyAttr)
        print(f"Bound HumanbodyAttr to '{args.name}'")

        # HumanIKTargetDoMove
        hb.HumanIKTargetDoMove(index=0, position=[0.05, 0.0, 0.0], duration=0.5, speed_based=True, relative=True)
        step(env, 12); print("HumanIKTargetDoMove executed")

        # HumanIKTargetDoRotate
        hb.HumanIKTargetDoRotate(index=0, rotation=[0.0, 10.0, 0.0], duration=0.5, speed_based=True, relative=True)
        step(env, 12); print("HumanIKTargetDoRotate executed")

        # HumanIKTargetDoRotateQuaternion
        hb.HumanIKTargetDoRotateQuaternion(index=0, quaternion=[0.0, 0.0, 0.0, 1.0], duration=0.5, speed_based=True, relative=True)
        step(env, 12); print("HumanIKTargetDoRotateQuaternion executed")

        # HumanIKTargetDoComplete
        hb.HumanIKTargetDoComplete(index=0)
        step(env, 3); print("HumanIKTargetDoComplete executed")

        # HumanIKTargetDoKill
        hb.HumanIKTargetDoKill(index=0)
        step(env, 3); print("HumanIKTargetDoKill executed")

        print("\nAll HumanbodyAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
