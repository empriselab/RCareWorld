"""Dressing environment for the PhyRC competition."""

from pyrcareworld.envs.base_env import RCareWorld
from pathlib import Path


_TEMPLATE_PATH = Path(__file__).parents[3] / "template"
_EXECUTABLE_PATH = _TEMPLATE_PATH / "Dressing" / "DressingPlayer.x86_64"


class DressingEnv(RCareWorld):
    """Dressing environment for the PhyRC competition."""

    def __init__(self, *args, **kwargs):
        super().__init__(executable_file=str(_EXECUTABLE_PATH), *args, **kwargs)
