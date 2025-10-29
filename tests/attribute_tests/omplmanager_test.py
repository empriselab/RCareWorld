from pathlib import Path
import argparse, time, os, sys
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
    ap = argparse.ArgumentParser(description="Test OmplManagerAttr methods (attribute-layer only)")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="OmplManager")
    ap.add_argument("--robot-id", type=int, default=221582)
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

        mgr = env.InstanceObject(name=args.name, attr_type=attr.OmplManagerAttr)
        print(f"Bound OmplManagerAttr to '{args.name}'")

        # modify_robot
        mgr.modify_robot(args.robot_id); step(env, 5); print("modify_robot executed")

        # set_state
        n = mgr.joint_num or (mgr.robot_attr.data or {}).get("number_of_moveable_joints", 0)
        if not n:
            print("No movable joints reported; aborting attribute test"); return
        zero = [0.0] * int(n)
        mgr.set_state(zero); step(env, 5); print("set_state executed")

        # get_cur_state
        cur = mgr.get_cur_state()
        print("get_cur_state executed:", cur if isinstance(cur, list) else "None")

        # reset
        mgr.reset(); step(env, 5); print("reset executed")

        # RestoreRobot
        mgr.RestoreRobot(args.robot_id); step(env, 5); print("RestoreRobot executed")

        print("\nAll OmplManagerAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
