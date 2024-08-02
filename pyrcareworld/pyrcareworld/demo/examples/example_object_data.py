from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

env = RCareWorld(assets=["Rigidbody_Box", "franka_panda"])

box = env.InstanceObject(name="Rigidbody_Box", id=123456, attr_type=attr.RigidbodyAttr)
box.SetTransform(position=[0, 1, 0])
env.step(5)
for key in box.data:
    print(key)
    print(box.data[key])

robot = env.InstanceObject(
    name="franka_panda", id=789789, attr_type=attr.ControllerAttr
)
robot.SetTransform(position=[1, 0, 0])
env.step()
for key in robot.data:
    print(key)
    print(robot.data[key])
env.close()
