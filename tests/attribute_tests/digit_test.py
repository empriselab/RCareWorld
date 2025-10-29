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
    ap = argparse.ArgumentParser(description="Test DigitAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="DigitTestObject")
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

        digit = env.InstanceObject(name=args.name, attr_type=attr.DigitAttr)
        print(f"Bound DigitAttr to '{args.name}'")

        # GetData
        digit.GetData(); step(env, 10); print("GetData executed")

        data = digit.data or {}
        if "light" in data:
            Path("digit_light.bin").write_bytes(data["light"])
            print("Saved digit_light.bin")
        if "depth" in data:
            Path("digit_depth.bin").write_bytes(data["depth"])
            print("Saved digit_depth.bin")

        print("\nAll DigitAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()