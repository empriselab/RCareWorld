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
    ap = argparse.ArgumentParser(description="Test GraspSimAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--name", default="GraspSimTestObject")
    ap.add_argument("--mesh", required=True, help="Absolute path to a .obj mesh")
    ap.add_argument("--gripper", default="ParallelGripper")
    ap.add_argument("--warmup", type=int, default=20)
    args = ap.parse_args()

    player = str(Path(args.player).expanduser().resolve())
    if not Path(player).exists():
        print("Player not found:", player); return
    if os.name != "nt":
        os.chmod(player, os.stat(player).st_mode | 0o111)

    mesh_path = str(Path(args.mesh).expanduser().resolve())
    if not Path(mesh_path).exists():
        print("Mesh not found:", mesh_path); return

    env = RCareWorld(executable_file=player)
    try:
        step(env, args.warmup)

        gs = env.InstanceObject(name=args.name, attr_type=attr.GraspSimAttr)
        print(f"Bound GraspSimAttr to '{args.name}'")

        # StartGraspSim
        points = [[0.0, 0.0, 0.02], [0.01, 0.0, 0.02], [-0.01, 0.0, 0.02]]
        normals = [[0.0, 0.0, -1.0]] * len(points)
        gs.StartGraspSim(
            mesh=mesh_path,
            gripper=args.gripper,
            points=points,
            normals=normals,
            depth_range_min=0.0,
            depth_range_max=0.03,
            depth_lerp_count=3,
            angle_lerp_count=3,
            parallel_count=16
        ); step(env, 20); print("StartGraspSim executed")

        # GenerateGraspPose
        gs.GenerateGraspPose(
            mesh=mesh_path,
            gripper=args.gripper,
            points=points,
            normals=normals,
            depth_range_min=0.0,
            depth_range_max=0.03,
            depth_lerp_count=3,
            angle_lerp_count=3
        ); step(env, 20); print("GenerateGraspPose executed")

        # StartGraspTest
        q = [0.0, 0.0, 0.0, 1.0]
        quats = [q for _ in points]
        gs.StartGraspTest(
            mesh=mesh_path,
            gripper=args.gripper,
            points=points,
            quaternions=quats,
            parallel_count=16
        ); step(env, 20); print("StartGraspTest executed")

        # ShowGraspPose
        gs.ShowGraspPose(
            mesh=mesh_path,
            gripper=args.gripper,
            positions=points,
            quaternions=quats
        ); step(env, 10); print("ShowGraspPose executed")

        data = gs.data or {}
        done = data.get("done", None)
        cnt = len(data.get("points", [])) if isinstance(data.get("points", []), list) else 0
        print("done:", done, "grasp_count:", cnt)

        print("\nAll GraspSimAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
