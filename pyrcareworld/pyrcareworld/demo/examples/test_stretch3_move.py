from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

def test_stretch3_move():
    """Tests loading and movement of the stretch 3 robot."""

    env = RCareWorld(assets=["stretch-3"], graphics=False)

    stretch = env.InstanceObject(name="stretch-3", attr_type=attr.ControllerAttr)
    stretch.SetTransform(position=[0, 0.05, 0])
    stretch.SetImmovable(False)
    env.step()

    for _ in range(3):
        stretch.TurnLeft(90, 30)
        env.step(300)
