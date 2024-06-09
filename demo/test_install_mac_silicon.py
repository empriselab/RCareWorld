from pyrcareworld.envs import RCareWorld
import os

"""
Make sure you have run the following commands in the terminal before running this script:
`arch -x86_64 bash` if your shell is bash
or 
`arch -x86_64 zsh` if your shell is zsh
"""
# run the bash command 'xattr -c Build/TestInstall/Mac/loadObject.app'
os.system('xattr -c Build/TestInstall/Mac/loadObject.app')

# Create a connection with the RCareWorld simulation environment
env = RCareWorld(executable_file="Build/TestInstall/Mac/loadObject.app", assets=["Cube"])

# Create a cube object
cube = env.create_object(id=12345, name="Cube", is_in_scene=False)
# Load the cube object
cube.load()

# Run the simulation for 5 steps, and print the data from the instance channel
for i in range(5):
    env._step()
    print(env.instance_channel.data)

# Change the position of the cube object
cube.setTransform([0, 0, 0])
# Run the simulation for 50 steps
env.stepSeveralSteps(50)
# Change the position of the cube object
cube.setTransform([1, 1, 1])
# Run the simulation for 50 steps
env.stepSeveralSteps(50)

# Create a new cube object by copying the original cube object
new_cube = cube.copy(1234560)
# Change the position of the new cube object
new_cube.setTransform([-1, 1, 0])
# Run the simulation for 50 steps
env.stepSeveralSteps(50)
# Destroy the new cube object
new_cube.destroy()

# Rotate the original cube object
for i in range(200):
    cube.setTransform(rotation=[0, 0, 0 + i])
    env.stepSeveralSteps(1)

# Close the connection with the RCareWorld simulation environment
env.close()

