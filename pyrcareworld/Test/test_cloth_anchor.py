from pyrcareworld.envs.base_env import RCareWorld

# Script to test cloth anchoring.
if __name__ == "__main__":
    env = RCareWorld()

    # Create a new cloth representation.
    cloth = env.create_cloth(id=100, name="Cloth", is_in_scene=True)

    # Anchors the cloth's particle group "corner" to the object with id 200.
    cloth.addParticleAnchor("corner", 200)

    # Step 100 times.
    for _ in range(100):
        env.step()

    # Unanchor. Observe the cloth fall.
    cloth.removeParticleAnchor("corner")

    # Continue stepping.
    for _ in range(10000):
        env.step()
