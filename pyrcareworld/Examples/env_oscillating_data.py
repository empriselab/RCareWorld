from pyrcareworld.envs import RCareWorld
import math

DELAY_STEPS = 30
AMPLITUDE = 0.5
PERIOD = 100

if __name__ == "__main__":
    env = RCareWorld()
    cube = env.create_object(id=99, name="Velcro", is_in_scene=False)
    initial_pos = cube.getPosition()

    iter = 0

    for _ in range(DELAY_STEPS):
        env.step()

    while True:
        sin_offset = AMPLITUDE * math.sin(iter / PERIOD * 2 * math.pi)
        cube.setTransform(
            position=[initial_pos[0], initial_pos[1], initial_pos[2] + sin_offset]
        )

        iter += 1

        env.step()
