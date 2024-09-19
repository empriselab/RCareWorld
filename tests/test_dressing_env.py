"""Tests for the dressing environment."""

from pyrcareworld.envs.dressing_env import DressingEnv


def test_dressing_env_initialization():
    """Tests that the dressing environment initializes without crashing."""
    env = DressingEnv(graphics=False)
    assert isinstance(env, DressingEnv)

def test_dressing_env_cloth_access():
    """Tests that the cloth is present in the dressing environment."""
    env = DressingEnv(graphics=False)
    cloth = env.get_cloth()
    assert cloth is not None

def test_dressing_env_cloth_particles():
    """Tests that the cloth particles are present in the dressing environment."""
    env = DressingEnv(graphics=False)
    cloth = env.get_cloth()
    cloth.GetParticles()
    env.step()
    cloth_particles = cloth.data['particles']  # Assuming cloth has a 'data' attribute with 'particles'
    assert cloth_particles is not None
    assert len(cloth_particles) > 0  # Ensure there are particles present