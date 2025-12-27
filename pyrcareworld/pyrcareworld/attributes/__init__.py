from pyrcareworld.attributes.base_attr import BaseAttr
from pyrcareworld.attributes.camera_attr import CameraAttr
from pyrcareworld.attributes.gameobject_attr import GameObjectAttr
from pyrcareworld.attributes.light_attr import LightAttr
from pyrcareworld.attributes.collider_attr import ColliderAttr
from pyrcareworld.attributes.controller_attr import ControllerAttr
from pyrcareworld.attributes.person_randomizer_attr import PersonRandomizerAttr
from pyrcareworld.attributes.rigidbody_attr import RigidbodyAttr
from pyrcareworld.attributes.cloth_attr import ClothAttr
from pyrcareworld.attributes.pointcloud_attr import PointCloudAttr
from pyrcareworld.attributes.custom_attr import CustomAttr
from pyrcareworld.attributes.activelightsensor_attr import ActiveLightSensorAttr
from pyrcareworld.attributes.digit_attr import DigitAttr
from pyrcareworld.attributes.gelslim_attr import GelSlimAttr
from pyrcareworld.attributes.humanbody_attr import HumanbodyAttr
from pyrcareworld.attributes.graspsim_attr import GraspSimAttr
from pyrcareworld.attributes.softbody_attr import SoftBodyAttr
# from pyrcareworld.attributes.intersect_attr import IntersectAttr
from pyrcareworld.attributes.cloth_grasper_attr import ClothGrasperAttr
# from pyrcareworld.attributes.move_detectopm_attr import MovementDetectionAttr
# from pyrcareworld.attributes.sponge_attr import SpongeAttr
from pyrcareworld.attributes.bathing_score_attr import BathingScoreAttr
from pyrcareworld.attributes.dressing_score_attr import DressingScoreAttr
from pyrcareworld.attributes.sponge_attr import SpongeAttr
from pyrcareworld.attributes.sponge_score_attr import SpongeScoreAttr
from pyrcareworld.attributes.collision_force_attr import CollisionForceAttr
from pyrcareworld.attributes.sponge_force_attr import SpongeForceAttr
from pyrcareworld.attributes.articulated_joint_attr import ArticulatedJointAttr
from pyrcareworld.attributes.arm_pose_iou_attr import ArmPoseIoUAttr
from pyrcareworld.attributes.collision_painter_attr import CollisionPainterAttr
from pyrcareworld.attributes.ink_canvas_attr import InkCanvasAttr
from pyrcareworld.attributes.sponge_attr import FMActionAttr

# THIS IS AN OPTIONAL FUNCTION, WON'T AFFECT YOUR USE
try:
  from pyrcareworld.attributes.omplmanager_attr import OmplManagerAttr
except ImportError:
  print("""Unable to import OmplManagerAttr. OMPL is an optional function that likely will not affect your use.""")


attrs = {
"BaseAttr": BaseAttr,
"CameraAttr": CameraAttr,
"GameObjectAttr": GameObjectAttr,
"LightAttr": LightAttr,
"ColliderAttr": ColliderAttr,
"ControllerAttr": ControllerAttr,
"RigidbodyAttr": RigidbodyAttr,
"ClothAttr": ClothAttr,
"PointCloudAttr": PointCloudAttr,
"CustomAttr": CustomAttr,
"ActiveLightSensorAttr": ActiveLightSensorAttr,
"DigitAttr": DigitAttr,
"GelSlimAttr": GelSlimAttr,
"HumanbodyAttr": HumanbodyAttr,
"GraspSimAttr": GraspSimAttr,
"SoftBodyAttr": SoftBodyAttr,
# "IntersectAttr": IntersectAttr,
"ClothGrasperAttr": ClothGrasperAttr,
"SpongeScoreAttr": SpongeScoreAttr,
"BathingScoreAttr": BathingScoreAttr,
"DressingScoreAttr": DressingScoreAttr,
"SpongeAttr": SpongeAttr,
"PersonRandomizerAttr": PersonRandomizerAttr,
"CollisionForceAttr": CollisionForceAttr,
"SpongeForceAttr": SpongeForceAttr,
"ArticulatedJointAttr": ArticulatedJointAttr,
"ArmPoseIoUAttr": ArmPoseIoUAttr,
"CollisionPainterAttr": CollisionPainterAttr,
"InkCanvasAttr": InkCanvasAttr,
"FMActionAttr": FMActionAttr,
}

if "OmplManagerAttr" in locals():
  attrs["OmplManagerAttr"] = OmplManagerAttr
