from pyrcareworld.envs import RCareWorld
import math

DELAY_STEPS = 30
AMPLITUDE = 0.5
PERIOD = 100

# Example for oscillating a cloth anchor back and forth and reading force data.
if __name__ == "__main__":
    env = RCareWorld()
    cube = env.create_object(id=99, name="Velcro", is_in_scene=True)
    cloth = env.create_cloth(id=800, name="LessVertices2Hole", is_in_scene=True)
    initial_pos = cube.getPosition()

    iter = 0

    for _ in range(DELAY_STEPS):
        env.step()

    while True:
        sin_offset = AMPLITUDE * math.sin(iter / PERIOD * 2 * math.pi)
        cube.setTransform(
            position=[initial_pos[0], initial_pos[1], initial_pos[2] + sin_offset]
        )

        forces = env.instance_channel.data[800]["forces"]
        if len(forces) > 0:
            print("Force:", forces)

        iter += 1

        env.step()
