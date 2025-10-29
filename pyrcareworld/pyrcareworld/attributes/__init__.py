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
from pyrcareworld.attributes.cloth_grasper_attr import ClothGrasperAttr
from pyrcareworld.attributes.sponge_attr import SpongeAttr

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
"ClothGrasperAttr": ClothGrasperAttr,
"SpongeAttr": SpongeAttr,
"PersonRandomizerAttr": PersonRandomizerAttr,
}

if "OmplManagerAttr" in locals():
  attrs["OmplManagerAttr"] = OmplManagerAttr
