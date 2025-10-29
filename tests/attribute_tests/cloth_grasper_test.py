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
    ap = argparse.ArgumentParser(description="Test ClothGrasperAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--grasper", default="ClothGrasperTestObject")
    ap.add_argument("--cloth", default="ClothTestObject")
    ap.add_argument("--robot", default="RobotTestObject")
    ap.add_argument("--gripper", default="Gripper")
    ap.add_argument("--radius", type=float, default=0.05)
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

        grasper = env.InstanceObject(name=args.grasper, attr_type=attr.ClothGrasperAttr)
        print(f"Bound ClothGrasperAttr to '{args.grasper}'")

        cloth_obj = env.InstanceObject(name=args.cloth, attr_type=attr.BaseAttr)
        robot_obj = env.InstanceObject(name=args.robot, attr_type=attr.BaseAttr)
        cloth_id = getattr(cloth_obj, "id", None)
        robot_id = getattr(robot_obj, "id", None)
        if cloth_id is None or robot_id is None:
            print("Could not resolve cloth/robot ids; check object names."); return

        # set_cloth_and_robot
        grasper.set_cloth_and_robot(
            cloth_id=int(cloth_id),
            cloth_name=args.cloth,
            robot_id=int(robot_id),
            gripper_name=args.gripper,
            grasp_radius=float(args.radius),
        ); step(env, 5); print("set_cloth_and_robot executed")

        # is_garment_being_held
        held0 = grasper.is_garment_being_held(); print("is_garment_being_held:", held0)

        # toggle_grasp_and_gripper
        grasper.toggle_grasp_and_gripper(); step(env, 10); print("toggle_grasp_and_gripper executed (1)")

        # is_garment_being_held
        held1 = grasper.is_garment_being_held(); print("is_garment_being_held:", held1)

        # toggle_grasp_and_gripper
        grasper.toggle_grasp_and_gripper(); step(env, 10); print("toggle_grasp_and_gripper executed (2)")

        # is_garment_being_held
        held2 = grasper.is_garment_being_held(); print("is_garment_being_held:", held2)

        print("\nAll ClothGrasperAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
