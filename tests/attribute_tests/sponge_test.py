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
    ap = argparse.ArgumentParser(description="Test SpongeAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="SpongeTestObject")
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--frames", type=int, default=30)
    ap.add_argument("--interval", type=float, default=0.02)
    ap.add_argument("--buffer", type=int, default=5, help="Frames of zero to tolerate before resetting reading to 0.0")
    args = ap.parse_args()

    player = str(Path(args.player).expanduser().resolve())
    if not Path(player).exists():
        print("Player not found:", player); return
    if os.name != "nt":
        os.chmod(player, os.stat(player).st_mode | 0o111)

    env = RCareWorld(executable_file=player)
    try:
        step(env, args.warmup)

        sp = env.GetAttr(id=91846)
        print(f"Bound SpongeAttr to '{args.name}'")

        # Initialize buffer parameters if exposed on the attr
        if hasattr(sp, "NUM_ZEROS_TO_RESET"):
            sp.NUM_ZEROS_TO_RESET = int(args.buffer)
            sp.LAST_NONZERO = [0.0]
            sp.NUM_ZERO_CURRENTLY = 0

        # GetPaintProportion
        p0 = sp.GetPaintProportion(); print("GetPaintProportion executed:", p0)

        # GetEffectiveForceProportion
        ef0 = sp.GetEffectiveForceProportion(); print("GetEffectiveForceProportion executed:", ef0)

        # GetForce (continuous stream)
        print("GetForce executed (stream):")
        for i in range(args.frames):
            step(env, 1, args.interval)
            f = sp.GetForce()
            fv = f[0] if isinstance(f, (list, tuple)) and len(f) else f
            print(f"frame {i+1:03d}: {fv}")

        # Optional: raw data fields snapshot
        data = sp.data or {}
        if "forces" in data:
            print("forces snapshot:", data["forces"])
        if "real_time_force" in data:
            print("real_time_force snapshot:", data["real_time_force"])
        if "paint_proportion" in data:
            print("paint_proportion snapshot:", data["paint_proportion"])
        if "effective_force_proportion" in data:
            print("effective_force_proportion snapshot:", data["effective_force_proportion"])

        print("\nAll SpongeAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
