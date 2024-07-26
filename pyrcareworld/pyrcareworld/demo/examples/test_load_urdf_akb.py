from pyrcareworld.envs.base_env import RCareWorld
import os

env = RCareWorld()

akb = env.LoadURDF(
    path=os.path.abspath(
        "../URDF/01b24b02-0e4e-11ed-81d4-ec2e98c7e246/motion_unity.urdf"
    ),
    native_ik=False,
)
akb.SetTransform(position=[0, 1, 0])
env.step()
env.SetViewTransform(position=[0, 1, 0.5])
env.ViewLookAt(akb.data["position"])
env.ShowArticulationParameter(akb.id)

env.Pend()
