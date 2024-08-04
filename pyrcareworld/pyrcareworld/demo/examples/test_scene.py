from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

env = RCareWorld(assets=["Collider_Box", "Rigidbody_Sphere"], executable_file="C:\\Users\\15156\\Desktop\\New folder (2)\\Rcareworld.exe")

box1 = env.InstanceObject(name="Collider_Box", attr_type=attr.ColliderAttr)
box1.SetTransform(position=[-0.5, 0.5, 0], scale=[0.1, 1, 1])
box2 = env.InstanceObject(name="Collider_Box", attr_type=attr.ColliderAttr)
box2.SetTransform(position=[0.5, 0.5, 0], scale=[0.1, 1, 1])
box3 = env.InstanceObject(name="Collider_Box", attr_type=attr.ColliderAttr)
box3.SetTransform(position=[0, 0.5, 0.5], scale=[1, 1, 0.1])
box4 = env.InstanceObject(name="Collider_Box", attr_type=attr.ColliderAttr)
box4.SetTransform(position=[0, 0.5, -0.5], scale=[1, 1, 0.1])
sphere = env.InstanceObject(name="Rigidbody_Sphere", attr_type=attr.RigidbodyAttr)
sphere.SetTransform(position=[0, 0.5, 0], scale=[0.5, 0.5, 0.5])
env.Pend()

env.SaveScene("test_scene.json")
env.ClearScene()
env.Pend()

env.LoadSceneAsync("test_scene.json")
env.Pend()
env.close()
