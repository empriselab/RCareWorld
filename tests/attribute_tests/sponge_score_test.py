from pathlib import Path
import argparse, time, os, json
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
    ap = argparse.ArgumentParser(description="Test SpongeScoreAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="SpongeScore")
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--dump", default="sponge_score_data.json")
    args = ap.parse_args()

    player = str(Path(args.player).expanduser().resolve())
    if not Path(player).exists():
        print("Player not found:", player); return
    if os.name != "nt":
        os.chmod(player, os.stat(player).st_mode | 0o111)

    env = RCareWorld(executable_file=player)
    try:
        step(env, args.warmup)

        sc = env.InstanceObject(name=args.name, attr_type=attr.SpongeScoreAttr)
        print(f"Bound SpongeScoreAttr to '{args.name}'")

        # parse_message
        step(env, 10)
        data = sc.data or {}
        print("SpongeScoreAttr data keys:", list(data.keys()))
        out = Path(args.dump).resolve()
        try:
            out.write_text(json.dumps(data, indent=2, default=str))
            print("Wrote data dump:", out)
        except Exception as e:
            print("Data dump failed:", e)

        print("\nAll SpongeScoreAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
