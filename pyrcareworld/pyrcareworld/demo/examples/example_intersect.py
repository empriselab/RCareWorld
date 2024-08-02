import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.intersect_attr import IntersectAttr

env = RCareWorld()
env.step()

intersect = env.InstanceObject(name="IntersectAttr", attr_type=IntersectAttr)

position_a = [0, 1, 0]
scale_a = [1, 1, 1]
position_b = [0.5, 1, 0]
scale_b = [1, 1, 1]

intersect.create_game_objects(position_a, scale_a, position_b, scale_b)
env.step()

is_intersected, ratio = intersect.check_intersection()
env.step()

print(f"Is Intersected: {is_intersected}")
print(f"Intersection Ratio: {ratio}")

env.close()
