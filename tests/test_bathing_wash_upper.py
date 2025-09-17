import os
import sys
import random
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld
from test_save_data_diffpolicy import init_data_saver, save_step_data, start_new_episode, finalize_data_saving

# Enable data saving (set to False to disable)
ENABLE_DATA_SAVING = True

# Enable SSH remote connection (set to True to use remote Unity)
USE_REMOTE = False

# Configure environment based on connection mode
if USE_REMOTE:
    # Remote mode: Unity runs on a different machine
    env = RCareWorld(
        bind_address="0.0.0.0",
        remote_mode=True,
        port=5004
    )
    print("[Remote Mode] Waiting for Unity connection on 0.0.0.0:5004")
    print("[Remote Mode] Make sure Unity is running and configured to connect to this server")
else:
    # Local mode: Unity runs on the same machine
    env = RCareWorld()

# Set high frequency time step for smooth simulation (0.01s = 100Hz)
env.SetTimeStep(0.01)

# Create an instance of the Franka Panda robot and set its IK target offset
robot = env.GetAttr(315893)

# robot.SetIKTargetOffset(position=[0, 0.105, 0])
env.step(200)

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(3158930)
gripper.GripperOpen()

# Initialize data saver for bathing wash task (save every 10 steps)
data_saver = init_data_saver(env, robot_id=315893, gripper_id=3158930,
<<<<<<< HEAD
                             enabled=ENABLE_DATA_SAVING, task_name="bathing_wash_upper", save_frequency=10)
=======
                             enabled=ENABLE_DATA_SAVING, task_name="bathing_wash_upper")
step_counter = 0
>>>>>>> parent of d3c71084... [Add] episode number

# Start first episode
if ENABLE_DATA_SAVING:
    start_new_episode()

initialize_target = env.GetAttr(5678)
env.step()
initialize_position = initialize_target.data["position"]

robot.IKTargetDoMove(
        position=initialize_position,
        duration=0,
        speed_based=False,
    )
robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)

shoulder_id = 3001
elbow_id = 3002
wrist_id = 3003

shoulder = env.GetAttr(shoulder_id)
elbow = env.GetAttr(elbow_id)
wrist = env.GetAttr(wrist_id)

shoulder_position = shoulder.data["position"]
elbow_position = elbow.data["position"]
wrist_position = wrist.data["position"]
env.step()

# shoulder to elbow
robot.IKTargetDoMove(
        position=[shoulder_position[0], shoulder_position[1]+0.1, shoulder_position[2]],
        duration=3,
        speed_based=False,
    )
# 150 steps for 3 seconds (3/0.02)
for i in range(150):
    env.step()
    step_counter += 1
    if i % 10 == 0:  # Save every 10 steps
        save_step_data(step_counter, {'phase': 'shoulder_position'})
robot.IKTargetDoMove(
        position=[elbow_position[0], elbow_position[1]+0.1, elbow_position[2]],
        duration=3,
        speed_based=False,
    )
for i in range(150):
    env.step()
    step_counter += 1
    if i % 10 == 0:  # Save every 10 steps
        save_step_data(step_counter, {'phase': 'elbow_position'})
# elbow to shoulder
robot.IKTargetDoMove(
        position=[shoulder_position[0], shoulder_position[1]+0.1, shoulder_position[2]],
        duration=3,
        speed_based=False,
    )
for i in range(150):
    env.step()
    step_counter += 1
    if i % 10 == 0:  # Save every 10 steps
        save_step_data(step_counter, {'phase': 'elbow_to_shoulder'})

robot.IKTargetDoMove(
        position=initialize_position,
        duration=3,
        speed_based=False,
    )
for i in range(150):
    env.step()
    step_counter += 1
    if i % 10 == 0:  # Save every 10 steps
        save_step_data(step_counter, {'phase': 'return_to_initial'})

# Finalize data saving before closing
finalize_data_saving()

env.Pend()





