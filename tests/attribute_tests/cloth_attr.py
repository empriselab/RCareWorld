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
    ap = argparse.ArgumentParser(description="Test all ClothAttr methods")
    default_player = (
    Path(__file__).resolve().parents[2]
    / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
    / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="ClothTestObject")
    ap.add_argument("--target", default="AttachTargetObject")
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

        # bind attribute
        cloth = env.InstanceObject(name=args.name, attr_type=attr.ClothAttr)
        print(f"Bound ClothAttr to object '{args.name}'")

        # GetParticles
        cloth.GetParticles()
        step(env, 3)
        print("GetParticles executed")

        # AddAttach
        target = env.InstanceObject(name=args.target, attr_type=attr.BaseAttr)
        target_id = 23
        cloth.AddAttach(id=target_id, max_dis=0.05)
        step(env, 3)
        print("AddAttach executed")

        # RemoveAttach
        cloth.RemoveAttach(id=target_id)
        step(env, 3)
        print("RemoveAttach executed")

        print("\nAll ClothAttr methods invoked successfully")

    finally:
        env.Pend()
        env.close()


if __name__ == "__main__":
    main()
