from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

def test_tobor_move():
    """Test moving a tobor robot."""
    env = RCareWorld(assets=["tobor_r300_ag95_ag95"], graphics=False)

    torbor = env.InstanceObject(name="tobor_r300_ag95_ag95", attr_type=attr.ControllerAttr)
    torbor.SetTransform(position=[0, 0.05, 0])
    torbor.SetImmovable(False)
    env.step()

    torbor.MoveForward(1, 0.2)
    env.step(300)
    torbor.TurnLeft(90, 30)
    env.step(300)
    torbor.MoveForward(1, 0.2)
    env.step(300)
    torbor.TurnLeft(90, 30)
    env.step(300)
    torbor.MoveForward(1, 0.2)
    env.step(300)
    torbor.TurnRight(90, 30)
    env.step(300)
    torbor.MoveBack(1, 0.2)
    env.step(300)
    torbor.TurnRight(90, 30)
    env.step(300)

    env.close()
