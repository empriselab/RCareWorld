import argparse
import threading
import time

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.base_attr import BaseAttr
from pyrcareworld.attributes.fm_action_attr import FMActionAttr
import pyrcareworld.attributes as attr


class _StepLoop(threading.Thread):
    def __init__(self, env, simulate):
        super().__init__(daemon=True)
        self.env = env
        self.simulate = simulate
        self.running = True

    def run(self):
        while self.running:
            try:
                self.env.step(simulate=self.simulate, collect=True)
            except Exception as exc:
                print(f"Step loop stopped: {exc}")
                break

    def stop(self):
        self.running = False


def _find_target(env, name_hint=None, target_id=None, wait_seconds=5.0):
    if target_id is not None:
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if target_id in env.attrs:
                return env.GetAttr(target_id)
            time.sleep(0.1)
        return None

    candidates = []
    for attr_id, inst in env.attrs.items():
        name = inst.data.get("name", "")
        type_name = inst.__class__.__name__
        if name_hint is None or name_hint in name or name_hint == type_name:
            candidates.append((attr_id, name))

    if not candidates:
        return None

    if len(candidates) > 1:
        print("Multiple candidates found:")
        for attr_id, name in candidates:
            print(f"  id={attr_id} name={name}")
        print("Using the first match.")

    return env.GetAttr(candidates[0][0])


def main():
    parser = argparse.ArgumentParser(description="Test FMActionAttr transfer actions.")
    parser.add_argument("--port", type=int, default=5004)
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--id", type=int, default=None)
    parser.add_argument("--name", type=str, default="TransferRemote")
    args = parser.parse_args()

    # Ensure Unity class name "TransferRemote" is recognized as FMActionAttr.
    attr.attrs["TransferRemote"] = FMActionAttr
    # Provide a fallback for Unity-only attrs not defined in Python.
    attr.attrs.setdefault("HumanArticulationAttr", BaseAttr)

    env = RCareWorld(port=args.port)
    stepper = _StepLoop(env, args.simulate)
    stepper.start()

    # Allow a few steps to populate attrs.
    time.sleep(1.0)

    target = _find_target(env, name_hint=args.name, target_id=args.id)
    if target is None:
        print("No TransferRemote attr found. Available attrs:")
        for attr_id, inst in env.attrs.items():
            name = inst.data.get("name", "")
            print(f"  id={attr_id} type={inst.__class__.__name__} name={name}")
        print("Try --name or --id after checking Unity IDs.")
        stepper.stop()
        env.close()
        return

    if not isinstance(target, FMActionAttr):
        target = target.SetType(FMActionAttr)

    print(f"Using attr id={target.id} name={target.data.get('name', '')}")
    actions = [
        ("align_lift_to_bed", lambda: target.align_lift_to_bed("Bed", 0.1)),
        ("load_patient_on_lift", lambda: target.load_patient_on_lift()),
        ("raise_lift", lambda: target.raise_lift(0.5)),
        ("align_lift_to_destination", lambda: target.align_lift_to_destination("Wheelchair", 0.1)),
        ("lower_lift", lambda: target.lower_lift(0.5)),
        ("unload_patient_from_lift", lambda: target.unload_patient_from_lift()),
        ("remove_lift", lambda: target.remove_lift("Lift", 0.1)),
    ]

    for name, fn in actions:
        try:
            input(f"Press Enter to run {name} (Ctrl+C to quit) ")
        except (EOFError, KeyboardInterrupt):
            break
        print(f"Run: {name}")
        fn()

    try:
        input("All actions queued. Press Enter to exit (Ctrl+C to quit) ")
    except (EOFError, KeyboardInterrupt):
        pass

    stepper.stop()
    env.close()


if __name__ == "__main__":
    main()
