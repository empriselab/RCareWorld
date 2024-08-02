import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.move_detectopm_attr import MovementDetectionAttr

env = RCareWorld()
env.step()

object = env.InstanceObject(name="MovementDetectionObject", attr_type=MovementDetectionAttr)

object.SetTransform(position=[0, 0, 0], rotation=[0, 0, 0])
env.step()

object.start_detection(detection_time=5.0)
env.step()

for _ in range(50):
    object.SetTransform(position=[0, 0.1, 0], rotation=[0, 1, 0], is_world=False)
    env.step()
    time.sleep(0.1)

position_difference, rotation_difference = object.get_movement_results()
env.step()

print(f"Position Difference: {position_difference}")
print(f"Rotation Difference: {rotation_difference}")

env.close()
