from pyrcareworld.envs import RCareWorld

env = RCareWorld()
cube = env.create_object(id=12345, name="Cube", is_in_scene=False)
ball = env.create_object(id=67890, name="Sphere", is_in_scene=True)
cube.load()
cube.setTransform([0, 0, 0])
env.stepSeveralSteps(5)
cube.setTransform([1, 1, 1])
env.stepSeveralSteps(5)


new_cube = cube.copy(1234560)
new_cube.setTransform([0, 0, 2])
env.stepSeveralSteps(10)
new_cube.destroy()

for i in range(60):
    cube.setTransform(rotation=[0, 0, 0 + i])
    env.stepSeveralSteps(1)

cube.setParent(ball)
env.stepSeveralSteps(50)
cube.unsetParent()
env.stepSeveralSteps(50)

ball.setActive(False)
env.stepSeveralSteps(50)
ball.setActive(True)
env.stepSeveralSteps(50)
ball.destroy()
env.stepSeveralSteps(50)
cube.destroy()
env.stepSeveralSteps(50)
env.close()
