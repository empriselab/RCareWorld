"""Tests that the main environments initialize without crashing."""

from pyrcareworld.envs.bathing_env import BathingEnv
from pyrcareworld.envs.dressing_env import DressingEnv


def test_bathing_env_initialization():
    """Tests that the bathing environment initializes without crashing."""
    env = BathingEnv(graphics=False)
    assert isinstance(env, BathingEnv)


def test_dressing_env_initialization():
    """Tests that the dressing environment initializes without crashing."""
    env = DressingEnv(graphics=False)
    assert isinstance(env, DressingEnv)
