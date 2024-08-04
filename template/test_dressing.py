import random
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import json

json_path = "Your Jason File(dressingscore.json) Path"
with open(json_path, 'r') as file:
    data = json.load(file)
    
"""
JSON File Template:
{
  "DressingScore": 0,
  "DressingScoreMax": 0,
  "DressingScoreMin": 0,
  "DressingScoreStep": 0,
  "DressingScoreThreshold": 0,
}

Print the data to see the keys and grades.
"""
# Initialize the environment with the specified assets and set the time step
env = RCareWorld(executable_file="Your Unity Executable Path")
env.SetTimeStep(0.005)


kinova_id = 315893
robot = env.GetAttr(kinova_id)
robot.SetPosition([1.267,1.148,0.716])
env.step()

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(3158930)
gripper.GripperOpen()


robot.WaitDo()

# Main loop to create, move, and manipulate boxes
while True:

    position1 = (1.907, 1.547, 0.33)
    position2 = (1.469, 1.547, 0.207)

    robot.IKTargetDoMove(
        position=[position1[0], position1[1] + 0.5, position1[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position1[0], position1[1], position1[2]],
        duration=2,
        speed_based=False,
    )
    robot.WaitDo()
    gripper.GripperClose()
    env.step(50)
    robot.IKTargetDoMove(
        position=[0, 0.5, 0], duration=2, speed_based=False, relative=True
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position2[0], position2[1] + 0.5, position2[2]],
        duration=4,
        speed_based=False,
    )
    robot.WaitDo()
    robot.IKTargetDoMove(
        position=[position2[0], position2[1] + 0.06, position2[2]],
        duration=2,
        speed_based=False,
    )
    
    for key, value in data.items():
        print(f'{key}: {value}')

    env.step()
