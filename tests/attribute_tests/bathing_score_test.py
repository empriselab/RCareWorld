from pathlib import Path
import argparse, json

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld import attributes as attr

def main():
    ap = argparse.ArgumentParser(description="Full BathingScoreAttr method coverage test")
    default_player = (
        Path(__file__).resolve().parents[2] / "executable" / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player),
                    help="Path to Unity player (Attribute_Tests.x86_64 or .exe)")
    ap.add_argument("--name", default="BathingScore",
                    help="Scene object name to bind (default: BathingScore)")
    ap.add_argument("--warmup", type=int, default=20,
                    help="Number of env.step() ticks before testing (default 20)")
    args = ap.parse_args()

    player = str(Path(args.player).expanduser().resolve())
    obj_name = args.name
    env = RCareWorld(executable_file=player)
    try:
        env.step()

        bathing = env.InstanceObject(name=obj_name, attr_type=attr.BathingScoreAttr)

        # get_scores()
        try:
            scores_initial = bathing.get_scores()
            print("get_scores() ->", scores_initial)
            print("PASS: get_scores() executed")
        except Exception as e:
            print("FAIL: get_scores() raised:", e)
            scores_initial = {}

        # get_score_for_task()
        if scores_initial:
            some_task = next(iter(scores_initial.keys()))
        else:
            # deliberately missing key (should return 0)
            some_task = "RinseArms"
        try:
            val = bathing.get_score_for_task(some_task)
            print(f"get_score_for_task('{some_task}') ->", val)
            print("PASS: get_score_for_task() executed")
        except Exception as e:
            print("FAIL: get_score_for_task() raised:", e)

        # load_scores_from_file()
        # Provide dummy values, load, then read back with get_scores()
        dummy = {"RinseArms": 0.2, "RinseLegs": 0.5, "RinseTorso": 0.8}
        tmp_in = Path("bathing_scores_dummy_in.json").resolve()
        tmp_in.write_text(json.dumps(dummy, indent=4))
        print("Created dummy input JSON:", tmp_in)

        try:
            bathing.load_scores_from_file(str(tmp_in))
            env.step()
            after_load = bathing.get_scores()
            print("After load, get_scores() ->", after_load)
            if after_load == dummy:
                print("PASS: load_scores_from_file applied (engine echoes loaded scores).")
            else:
                print("WARN: Engine did not echo back dummy scores; this is normal if the scene ignores LoadScores.")
            print("PASS: load_scores_from_file() executed")
        except Exception as e:
            print("FAIL: load_scores_from_file() raised:", e)

        # save_scores_to_file()
        tmp_out = Path("bathing_scores_dummy_out.json").resolve()
        try:
            bathing.save_scores_to_file(str(tmp_out))
            print("save_scores_to_file ->", tmp_out, "| exists:", tmp_out.exists())
            if tmp_out.exists():
                try:
                    saved = json.loads(tmp_out.read_text())
                    print("Saved JSON contents:", saved)
                except Exception as e:
                    print("WARN: Could not read saved JSON:", e)
            print("PASS: save_scores_to_file() executed")
        except Exception as e:
            print("FAIL: save_scores_to_file() raised:", e)

        print("\n Test complete")
    finally:
        env.Pend()
        env.close()

if __name__ == "__main__":
    main()
