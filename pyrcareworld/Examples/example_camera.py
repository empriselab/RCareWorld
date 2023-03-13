from pyrcareworld.envs import RCareWorld

env = RCareWorld()
env.create_camera(id=123456, name='camera')
camera = env.get_camera(123456)
camera.load()
camera.setTransform(position = [0, 0.25, 0], rotation = [30, 0, 0])

env.close()