"""Dressing environment for the PhyRC competition."""

from pyrcareworld.envs.base_env import RCareWorld
from pathlib import Path

_TEMPLATE_PATH = Path(__file__).parents[3] / "template"
_DEFAULT_EXECUTABLE_PATH = _TEMPLATE_PATH / "Dressing" / "DressingPlayer.x86_64"

class DressingEnv(RCareWorld):
    """Dressing environment for the PhyRC competition."""

    # Environment-specific unity attribute IDs.
    _robot_id: int = 315893
    _gripper_id: int = 3158930
    _camera_id: int = 654321
    _cloth_id: int = 782563

    def __init__(self, executable_file=str(_DEFAULT_EXECUTABLE_PATH), *args, **kwargs):
        super().__init__(executable_file=executable_file, *args, **kwargs)

    def get_robot(self):
        """Access the robot."""
        return self.GetAttr(self._robot_id)
    
    def get_gripper(self):
        """Access the gripper."""
        return self.GetAttr(self._gripper_id)
    
    def get_camera(self):
        """Access the camera."""
        return self.GetAttr(self._camera_id)

    def get_cloth(self):
        """Access the cloth."""
        return self.GetAttr(self._cloth_id)