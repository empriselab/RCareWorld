from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.light_attr import LightType

env = RCareWorld(scene_file="LightScene.json")

light = env.GetAttr(885275)
env.SetShadowDistance(50)
while 1:
    env.step(50)
    light.SetColor(color=[1.0, 0.0, 0.0])
    env.step(50)
    light.SetRange(30.0)
    env.step(50)
    light.SetType(LightType.Directional)
    env.step(50)
    light.SetIntensity(5.0)
    env.step(50)
    light.SetType(LightType.Spot)
    env.step(50)
    light.SetSpotAngle(60.0)
    env.step(50)
    light.SetType(LightType.Point)
    env.step(50)
    light.SetRange(10.0)
    light.SetIntensity(1.0)
    light.SetSpotAngle(30.0)
