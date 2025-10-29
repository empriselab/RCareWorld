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
    ap = argparse.ArgumentParser(description="Test DressingScoreAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="DressingScore")
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

        dr = env.InstanceObject(name=args.name, attr_type=attr.DressingScoreAttr)
        print(f"Bound DressingScoreAttr to '{args.name}'")

        # get_scores
        scores0 = dr.get_scores(); step(env, 2); print("get_scores executed:", scores0)

        # get_score_for_task
        task_name = next(iter(scores0.keys())) if scores0 else "PutOnShirt"
        s_task = dr.get_score_for_task(task_name); step(env, 1); print("get_score_for_task executed:", task_name, "->", s_task)

        # load_scores_from_file
        dummy_in = Path("dressing_scores_dummy_in.json")
        dummy_payload = {"PutOnShirt": 0.4, "ZipJacket": 0.7}
        dummy_in.write_text(json.dumps(dummy_payload, indent=2))
        dr.load_scores_from_file(str(dummy_in)); step(env, 4); print("load_scores_from_file executed")

        # get_scores
        scores1 = dr.get_scores(); step(env, 2); print("get_scores executed:", scores1)

        # save_scores_to_file
        dummy_out = Path("dressing_scores_dummy_out.json")
        dr.save_scores_to_file(str(dummy_out)); step(env, 1); print("save_scores_to_file executed ->", dummy_out.resolve())

        print("\nAll DressingScoreAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()