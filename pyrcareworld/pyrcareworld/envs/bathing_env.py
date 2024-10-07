"""Bathing environment for the PhyRC competition."""

from pyrcareworld.attributes.camera_attr import CameraAttr
from pyrcareworld.attributes.controller_attr import ControllerAttr
from pyrcareworld.attributes.sponge_attr import SpongeAttr
from pyrcareworld.envs.base_env import RCareWorld
from pathlib import Path


_TEMPLATE_PATH = Path(__file__).parents[3] / "template"
_DEFAULT_EXECUTABLE_PATH = _TEMPLATE_PATH / "Bathing" / "BathingPlayer.x86_64"


class BathingEnv(RCareWorld):
    """Bathing environment for the PhyRC competition."""

    # Environment-specific unity attribute IDs.
    _gripper_id: int = 2215820
    _robot_id: int = 221582
    _camera_id: int = 654321
    _sponge_id: int = 91846

    def __init__(self, executable_file=str(_DEFAULT_EXECUTABLE_PATH), *args, **kwargs):
        super().__init__(executable_file=executable_file, *args, **kwargs)

    def get_robot(self) -> ControllerAttr:
        """Access the robot."""
        return self.GetAttr(self._robot_id)
    
    def get_gripper(self) -> ControllerAttr:
        """Access the gripper."""
        return self.GetAttr(self._gripper_id)
    
    def get_camera(self) -> CameraAttr:
        """Access the camera."""
        return self.GetAttr(self._camera_id)

    def get_sponge(self) -> SpongeAttr:
        """Access the sponge."""
        return self.GetAttr(self._sponge_id)
