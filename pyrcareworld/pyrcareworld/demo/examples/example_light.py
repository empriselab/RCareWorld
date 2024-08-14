print("""
This script demonstrates the dynamic manipulation of light properties within a scene in the RCareWorld environment.

What it Implements:
- Initializes the environment with a scene containing a light source.
- Continuously modifies the light's properties, including color, range, type (Directional, Spot, Point), intensity, and spot angle.

What the Functionality Covers:
- Understanding how to interact with and control light attributes in a simulated environment.
- Demonstrates the effects of different light settings on a scene.

Required Operations:
- Loop: The script continuously updates the light's properties in a loop.
- Property Manipulation: Changes various light settings to observe their effects on the scene.
""")

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.light_attr import LightType
from pyrcareworld.demo import executable_path

# Initialize the environment with the specified scene file
player_path = os.path.join(executable_path, "../executable/Player/Player.x86_64")

# Initialize the environment with the specified scene file
env = RCareWorld(scene_file="LightScene.json", executable_file=player_path)

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
