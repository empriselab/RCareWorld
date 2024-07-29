import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import os.path
from pyrcareworld.envs.base_env import RCareWorld
from demo import mesh_path

def test_cloth_attach():
    """Tests simulating a cloth."""
    env = RCareWorld(graphics=False)
    env.DebugObjectPose()
    env.EnabledGroundObiCollider(True)
    t_shirt_path = os.path.join(mesh_path, 'Tshirt.obj')
    mesh = env.LoadCloth(
        path=t_shirt_path
    )
    mesh.SetTransform(position=[0, 1, 0])
    env.step(200)
    mesh.GetParticles()
    env.step()
    print(mesh.data)
    position1 = mesh.data['particles'][500]
    position2 = mesh.data['particles'][200]
    point1 = env.InstanceObject("Empty")
    point1.SetTransform(position=position1)
    mesh.AddAttach(point1.id)
    point2 = env.InstanceObject("Empty")
    point2.SetTransform(position=position2)
    mesh.AddAttach(point2.id)
    env.step()

    point1.DoMove([-0.25, 1, 0], 2, speed_based=False)
    point2.DoMove([0.25, 1, 0], 2, speed_based=False)
    point2.WaitDo()

    for _ in range(3):
        point1.DoMove([-0.25, 1, -0.5], 1)
        point2.DoMove([0.25, 1, -0.5], 1)
        point2.WaitDo()

        point1.DoMove([-0.25, 1, 0.5], 1)
        point2.DoMove([0.25, 1, 0.5], 1)
        point2.WaitDo()

