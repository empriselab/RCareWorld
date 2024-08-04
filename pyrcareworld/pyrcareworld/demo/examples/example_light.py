from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.light_attr import LightType

# Initialize the environment with the specified scene file
env = RCareWorld(scene_file="LightScene.json", executable_file="C:\\Users\\15156\\Desktop\\New folder (2)\\Rcareworld.exe")

# Get the light attribute by ID
light = env.GetAttr(885275)

# Set the shadow distance
env.SetShadowDistance(50)

# Main loop to change light properties
while True:
    # Step the environment and set light color
    env.step(50)
    light.SetColor(color=[1.0, 0.0, 0.0])

    # Step the environment and set light range
    env.step(50)
    light.SetRange(30.0)

    # Step the environment and set light type to Directional
    env.step(50)
    light.SetType(LightType.Directional)

    # Step the environment and set light intensity
    env.step(50)
    light.SetIntensity(5.0)

    # Step the environment and set light type to Spot
    env.step(50)
    light.SetType(LightType.Spot)

    # Step the environment and set light spot angle
    env.step(50)
    light.SetSpotAngle(60.0)

    # Step the environment and set light type to Point
    env.step(50)
    light.SetType(LightType.Point)

    # Step the environment and reset light properties
    env.step(50)
    light.SetRange(10.0)
    light.SetIntensity(1.0)
    light.SetSpotAngle(30.0)
