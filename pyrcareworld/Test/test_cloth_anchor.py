from pyrcareworld.envs.rcareworld_env import RCareWorld

# Script to test cloth anchoring.
if __name__ == "__main__":
    env = RCareWorld()

    # Create a new cloth representation.
    cloth = env.create_cloth(id=100, name="Cloth", is_in_scene=True)

    # Anchors the cloth's particle group "corner" to the object with id 200.
    cloth.addParticleAnchor("corner", 200)

    cube = env.create_object(id=300, name="Average Indicator", is_in_scene=True)

    def fetch_and_set():
        """
        Fetches the hole particle positions and steps the environment,
        setting the average cube in the Unity world to the average position.
        """
        # Fetch particle positions on the next frame. Need to step before reading.
        cloth.fetchParticlePositions("hole")
        env.step()

        # Also test cloth particle group position retrieval.
        data = env.instance_channel.data[100]
        positions = data["particle_groups"]["hole"]
        average_position = [sum(x) / len(x) for x in zip(*positions)]

        # Set the cube to this average position in the world.
        cube.setTransform(position=average_position)

    # Step 200 times.
    for _ in range(200):
        fetch_and_set()

    # Unanchor. Observe the cloth fall.
    cloth.removeParticleAnchor("corner")

    # Continue stepping.
    for _ in range(10000):
        fetch_and_set()
