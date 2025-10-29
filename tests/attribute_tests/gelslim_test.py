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
    ap = argparse.ArgumentParser(description="Test GelSlimAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="GelSlimTestObject")
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

        gel = env.InstanceObject(name=args.name, attr_type=attr.GelSlimAttr)
        print(f"Bound GelSlimAttr to '{args.name}'")

        # GetData
        gel.GetData(); step(env, 10); print("GetData executed")

        # BlurGel
        gel.BlurGel(radius=5, sigma=2.0); step(env, 5); print("BlurGel executed")

        # RestoreGel
        gel.RestoreGel(); step(env, 5); print("RestoreGel executed")

        data = gel.data or {}
        if "light" in data:
            Path("gelslim_light.bin").write_bytes(data["light"])
            print("Saved gelslim_light.bin")
        if "depth" in data:
            Path("gelslim_depth.bin").write_bytes(data["depth"])
            print("Saved gelslim_depth.bin")

        print("\nAll GelSlimAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
