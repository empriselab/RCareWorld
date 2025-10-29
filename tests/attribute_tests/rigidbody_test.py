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
    ap = argparse.ArgumentParser(description="Test RigidbodyAttr methods")
    default_player = (
    Path(__file__).resolve().parents[2]
    / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
    / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="RigidbodyTestObject")
    ap.add_argument("--target", default="RigidbodyTargetObject")
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

        rb = env.InstanceObject(name=args.name, attr_type=attr.RigidbodyAttr)
        print(f"Bound RigidbodyAttr to '{args.name}'")

        # SetMass
        rb.SetMass(2.0); step(env, 3); print("SetMass executed")

        # SetDrag
        rb.SetDrag(0.2); step(env, 3); print("SetDrag executed")

        # SetAngularDrag
        rb.SetAngularDrag(0.05); step(env, 3); print("SetAngularDrag executed")

        # SetUseGravity
        rb.SetUseGravity(True); step(env, 3)
        rb.SetUseGravity(False); step(env, 3)
        rb.SetUseGravity(True); step(env, 3); print("SetUseGravity executed")

        # EnabledMouseDrag
        rb.EnabledMouseDrag(True); step(env, 3)
        rb.EnabledMouseDrag(False); step(env, 3); print("EnabledMouseDrag executed")

        # AddForce
        rb.AddForce([0, 5, 0]); step(env, 6); print("AddForce executed")

        # SetVelocity
        rb.SetVelocity([0, 0, 2]); step(env, 6); print("SetVelocity executed")

        # SetAngularVelocity
        rb.SetAngularVelocity([0, 2, 0]); step(env, 6); print("SetAngularVelocity executed")

        # SetKinematic
        rb.SetKinematic(True); step(env, 3)
        rb.SetKinematic(False); step(env, 3); print("SetKinematic executed")

        # Link
        target = env.InstanceObject(name=args.target, attr_type=attr.RigidbodyAttr)
        tgt_id = getattr(target, "id", None)
        if tgt_id is not None:
            rb.Link(target_id=int(tgt_id), joint_index=0, mass_scale=1.0, connected_mass_scale=1.0)
            step(env, 6); print("Link executed")
        else:
            print("Link skipped (target not found)")

        print("\nAll RigidbodyAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
