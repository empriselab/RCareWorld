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
    ap = argparse.ArgumentParser(description="Test ColliderAttr methods")
    default_player = (
    Path(__file__).resolve().parents[2]
    / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
    / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="ColliderTestObject")
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

        col = env.InstanceObject(name=args.name, attr_type=attr.ColliderAttr)
        print(f"Bound ColliderAttr to object '{args.name}'")

        # EnabledAllCollider
        col.EnabledAllCollider(True)
        step(env, 3)
        col.EnabledAllCollider(False)
        step(env, 3)
        col.EnabledAllCollider(True)
        step(env, 3)
        print("EnabledAllCollider executed")

        # SetPhysicMaterial
        col.SetPhysicMaterial(
            bounciness=0.3,
            dynamicFriction=0.6,
            staticFriction=0.7,
            frictionCombine=0,  # Average
            bounceCombine=1,    # Maximum
        )
        step(env, 3)
        print("SetPhysicMaterial executed")

        # SetRFMoveColliderActive
        col.SetRFMoveColliderActive(True)
        step(env, 3)
        col.SetRFMoveColliderActive(False)
        step(env, 3)
        col.SetRFMoveColliderActive(True)
        step(env, 3)
        print("SetRFMoveColliderActive executed")

        # GenerateVHACDColider
        col.GenerateVHACDColider()
        step(env, 5)
        print("GenerateVHACDColider executed")

        # AddObiCollider
        col.AddObiCollider()
        step(env, 3)
        print("AddObiCollider executed")

        print("\nAll ColliderAttr methods invoked successfully")

    finally:
        env.Pend()
        env.close()


if __name__ == "__main__":
    main()
