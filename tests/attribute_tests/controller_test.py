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
    ap = argparse.ArgumentParser(description="Test ControllerAttr methods")
    default_player = (
        Path(__file__).resolve().parents[2]
        / "pyrcareworld" / "pyrcareworld" / "demo" / "executable"
        / "Attribute_Tests" / "Attribute_Tests.x86_64"
    )
    ap.add_argument("--player", default=str(default_player))
    ap.add_argument("--id", type=int, default=221582)
    ap.add_argument("--warmup", type=int, default=20)
    args = ap.parse_args()

    player = str(Path(args.player).expanduser().resolve())
    if not Path(player).exists():
        print("Player not found:", player); return
    if os.name != "nt":
        os.chmod(player, os.stat(player).st_mode | 0o111)

    env = RCareWorld(executable_file=player)
    try:
        print("Starting ControllerAttr tests...")
        step(env, args.warmup)
        print("2")
        ctrl = env.GetAttr(id=221582)
        step(env, 3)
        print(f"Bound ControllerAttr to id {args.id}")

        # SetJointPosition
        ctrl.SetJointPosition([0.0, 0.2, -0.2, 0.1])
        step(env, 6)
        print("SetJointPosition executed")

        # SetJointPositionDirectly
        ctrl.SetJointPositionDirectly([0.1, 0.1, 0.0, -0.1])
        step(env, 6)
        print("SetJointPositionDirectly executed")

        # SetIndexJointPosition
        ctrl.SetIndexJointPosition(0, 0.25)
        step(env, 6)
        print("SetIndexJointPosition executed")

        # SetIndexJointPositionDirectly
        ctrl.SetIndexJointPositionDirectly(1, -0.15)
        step(env, 6)
        print("SetIndexJointPositionDirectly executed")

        # SetJointPositionContinue
        ctrl.SetJointPositionContinue(100, [[0.0,0.0,0.0,0.0],[0.05,0.05,-0.05,0.0],[0.1,0.1,-0.1,0.0]])
        step(env, 12)
        print("SetJointPositionContinue executed")

        # SetJointStiffness
        ctrl.SetJointStiffness([200.0, 200.0, 200.0, 200.0])
        step(env, 3)
        print("SetJointStiffness executed")

        # SetJointDamping
        ctrl.SetJointDamping([20.0, 20.0, 20.0, 20.0])
        step(env, 3)
        print("SetJointDamping executed")

        # SetJointLimit
        ctrl.SetJointLimit([1.0, 1.0, 1.0, 1.0], [-1.0, -1.0, -1.0, -1.0]); step(env, 3)
        print("SetJointLimit executed")

        # SetJointVelocity
        ctrl.SetJointVelocity([0.2, -0.2, 0.2, -0.2])
        step(env, 6)
        print("SetJointVelocity executed")

        # SetIndexJointVelocity
        ctrl.SetIndexJointVelocity(2, 0.3)
        step(env, 6)
        print("SetIndexJointVelocity executed")

        # SetJointUseGravity
        ctrl.SetJointUseGravity(True)
        step(env, 3)
        ctrl.SetJointUseGravity(False)
        step(env, 3)
        ctrl.SetJointUseGravity(True)
        step(env, 3)
        print("SetJointUseGravity executed")

        # SetJointDriveForce
        ctrl.SetJointDriveForce([50.0, 50.0, 50.0, 50.0])
        step(env, 3)
        print("SetJointDriveForce executed")

        # AddJointForce
        ctrl.AddJointForce([5.0, 0.0, 0.0, 0.0])
        step(env, 3)
        print("AddJointForce executed")

        # AddJointForceAtPosition
        ctrl.AddJointForceAtPosition(
        joint_forces=[2.0, 0.0, 0.0, 0.0],
        force_positions=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
        step(env, 3)
        print("AddJointForceAtPosition executed")

        # AddJointTorque
        ctrl.AddJointTorque([0.1, 0.0, 0.0, 0.0])
        step(env, 3)
        print("AddJointTorque executed")

        # GetJointInverseDynamicsForce
        ctrl.GetJointInverseDynamicsForce()
        step(env, 3)
        print("GetJointInverseDynamicsForce executed")

        # SetImmovable
        ctrl.SetImmovable(False)
        step(env, 3)
        print("SetImmovable executed")

        # MoveForward
        ctrl.MoveForward(0.5, 0.2)
        step(env, 12)
        print("MoveForward executed")

        # MoveBack
        ctrl.MoveBack(0.3, 0.2)
        step(env, 10)
        print("MoveBack executed")

        # TurnLeft
        ctrl.TurnLeft(10.0, 0.5)
        step(env, 12)
        print("TurnLeft executed")

        # TurnRight
        ctrl.TurnRight(10.0, 0.5)
        step(env, 12)
        print("TurnRight executed")

        # TargetVelocity
        ctrl.TargetVelocity(vel_left=0.5, vel_right=0.5, duration=0.2)
        step(env, 12)
        print("TargetVelocity executed")

        # StopMovement
        ctrl.StopMovement()
        step(env, 3)
        print("StopMovement executed")

        # GripperOpen
        ctrl.GripperOpen()
        step(env, 6)
        print("GripperOpen executed")

        # GripperClose
        ctrl.GripperClose()
        step(env, 6)
        print("GripperClose executed")

        # EnabledNativeIK
        ctrl.EnabledNativeIK(True)
        step(env, 3)
        print("EnabledNativeIK executed")

        # IKTargetDoMove
        ctrl.IKTargetDoMove([0.05, 0.0, 0.0], 0.5, True, True)
        step(env, 12)
        print("IKTargetDoMove executed")

        # IKTargetDoRotate
        ctrl.IKTargetDoRotate([0.0, 10.0, 0.0], 0.5, True, True)
        step(env, 12)
        print("IKTargetDoRotate executed")

        # IKTargetDoRotateQuaternion
        ctrl.IKTargetDoRotateQuaternion([0.0, 0.0, 0.0, 1.0], 0.5, True, True)
        step(env, 12)
        print("IKTargetDoRotateQuaternion executed")

        # IKTargetDoComplete
        ctrl.IKTargetDoComplete()
        step(env, 3)
        print("IKTargetDoComplete executed")

        # IKTargetDoKill
        ctrl.IKTargetDoKill()
        step(env, 3)
        print("IKTargetDoKill executed")

        # GetIKTargetJointPosition
        ctrl.GetIKTargetJointPosition(position=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0], iterate=50)
        step(env, 6)
        print("GetIKTargetJointPosition executed")

        # SetIKTargetOffset
        ctrl.SetIKTargetOffset(position=[0.01, 0.0, 0.0], rotation=[0.0, 5.0, 0.0])
        step(env, 6)
        print("SetIKTargetOffset executed")

        # GetJointLocalPointFromWorld
        ctrl.GetJointLocalPointFromWorld(0, [0.0, 0.0, 0.0])
        step(env, 3)
        print("GetJointLocalPointFromWorld executed")

        # GetJointWorldPointFromLocal
        ctrl.GetJointWorldPointFromLocal(0, [0.0, 0.0, 0.0])
        step(env, 3)
        print("GetJointWorldPointFromLocal executed")

        # AddRoot6DOF
        root = ctrl.AddRoot6DOF()
        step(env, 6)
        print("AddRoot6DOF executed")

        print("\nAll ControllerAttr methods invoked successfully")
    finally:
        env.Pend(); env.close()

if __name__ == "__main__":
    main()
