"""Tests for the dressing environment."""

from pyrcareworld.envs.dressing_env import DressingEnv


def test_dressing_env_initialization():
    """Tests that the dressing environment initializes without crashing."""
    env = DressingEnv(graphics=False)
    assert isinstance(env, DressingEnv)
