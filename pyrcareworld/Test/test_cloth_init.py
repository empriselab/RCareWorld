from pyrcareworld.envs.rcareworld_env import RCareWorld
import random

# Script to test cloth initial positions.
if __name__ == "__main__":
    env = RCareWorld()

    # Create a new cloth representation.
    cloth = env.create_cloth(id=100, name="Cloth", is_in_scene=True)

    # Every 200th step, sets the cloth particles to a random position in a cube around some random point in the scene.
    step = 0
    for _ in range(10000):
        env.step()
        step += 1

        if step % 200 == 0:
            # Make a random 3 vector in the range of [0, 1].
            random_pos = [random.uniform(0, 1) for _ in range(3)]

            positions = []

            # There happens to be 705 particles in this scene.
            for _ in range(705):
                random_relative_pos = [random.uniform(-0.2, 0.2) for _ in range(3)]

                my_pos = [a + b for a, b in zip(random_pos, random_relative_pos)]

                # Add the new position to the list.
                positions.append(my_pos)

            # Convert the list of positions to a mapping.
            positions = dict(enumerate(positions))

            cloth.initializeParticlePositions(positions)
