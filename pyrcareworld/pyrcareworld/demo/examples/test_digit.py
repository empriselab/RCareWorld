import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.digit_attr import DigitAttr

def test_digit():
    """Tests for the digit robot."""
    env = RCareWorld(graphics=False)

    digit = env.InstanceObject(name="Digit", attr_type=DigitAttr)
    digit.SetTransform(position=[0, 0.015, 0])
    target = env.InstanceObject(name="DigitTarget")
    target.SetTransform(position=[0, 0.05, 0.015])
    env.SetViewTransform(position=[-0.1, 0.033, 0.014], rotation=[0, 90, 0])
    env.close()
