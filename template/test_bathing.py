import json
from pyrcareworld.envs.base_env import RCareWorld
# from pyrcareworld.attributes.sponge_attr import SpongeAttr

# json_path = "Your Jason File(dressingscore.json) Path"
# with open(json_path, 'r') as file:
#     data = json.load(file)
    
# """
# JSON File Template:
# {
#     "PickUpScrubberScore": 0,
#     "DipScrubberInWaterTankScore": 0,
#     "MoveScrubberToManikinScore": 0,
#     "BodyCoverageScore": 0,
#     "ForceThresholdScore": 0,
#     "TotalScore": 0
# }

# Print the data to see the keys and grades.
# """
# Initialize the environment with the specified assets and set the time step
env = RCareWorld()#executable_file="Your Unity Executable Path"
# env.SetTimeStep(0.005)

stretch_id = 221582
robot = env.GetAttr(stretch_id)
env.step()

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(2215820)
gripper.GripperOpen()
env.step()

env.step(100)

gripper.GripperClose()
env.step()



sponge = env.GetAttr(91846)
env.step()
print(sponge.data)

# Main loop to create, move, and manipulate boxes
while True:


    # Random positions
    position1 = (-0.657, 0.941, 1.645)
    position2 = (-0.263, 1.063, 1.645)

    # Move the robot to the first box, pick it up, and move it to the second box's position
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

    print(sponge.data)
        

    # print(sponge.GetPaintProportion())
    # print(sponge.GetEffectiveForceProportion())
    # print(sponge.GetRealTimeForces())

    env.step()
