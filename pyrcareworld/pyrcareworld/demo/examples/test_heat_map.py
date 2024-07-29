from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import cv2
import numpy as np


def test_heat_map():
    """Test recording and generating heat maps."""
    env = RCareWorld()

    camera = env.InstanceObject(name="Camera", attr_type=attr.CameraAttr)
    camera.SetTransform(position=[-0.1, 0.033, 0.014], rotation=[0, 90, 0])
    target = env.InstanceObject(name="Rigidbody_Sphere", attr_type=attr.RigidbodyAttr)
    target.SetDrag(2)
    target.EnabledMouseDrag(True)
    target.SetUseGravity(False)
    target.SetTransform(position=[0, 0.05, 0.015], scale=[0.01, 0.01, 0.01])
    env.step()
    env.AlignCamera(camera.id)
    env.SendLog("Click End Pend button to start heat map record")
    env.Pend()
    camera.StartHeatMapRecord([target.id])
    env.SendLog("Drag the sphere to generate heat map")
    env.SendLog("Click End Pend button to end heat map record")
    env.Pend()
    camera.EndHeatMapRecord()
    camera.GetHeatMap()
    env.step()
    print(camera.data)
    print(camera.data["heat_map"])
    image_np = np.frombuffer(camera.data["heat_map"], dtype=np.uint8)
    image_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    print(image_np.shape)
    env.close()
    cv2.imshow("heatmap", image_np)
    cv2.waitKey(0)
