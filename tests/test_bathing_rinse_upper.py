import os
import sys
import random
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld
from test_save_data_diffpolicy import init_data_saver, save_step_data, start_new_episode, finalize_data_saving

# ================ CONFIGURATION PARAMETERS ================
# Enable data saving (set to False to disable)
ENABLE_DATA_SAVING = True

# Number of episodes to collect (default: 20)
EPISODE_NUMBER = 20

# Enable SSH remote connection (set to True to use remote Unity)
USE_REMOTE = True

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

# Initialize data saver for bathing rinse task (save every 10 steps)
data_saver = init_data_saver(env, robot_id=315893, gripper_id=3158930,
                             enabled=ENABLE_DATA_SAVING, task_name="bathing_rinse_upper", save_frequency=10)

print(f"🚀 Starting data collection for {EPISODE_NUMBER} episodes...")

# Execute multiple episodes
for episode in range(EPISODE_NUMBER):
    print(f"📊 Episode {episode + 1}/{EPISODE_NUMBER}")

    # Start new episode
    if ENABLE_DATA_SAVING:
        start_new_episode()

    step_counter = 0

    # Reset robot to initial position
    initialize_target = env.GetAttr(5678)
    env.step()
    initialize_position = initialize_target.data["position"]

    robot.IKTargetDoMove(
            position=initialize_position,
            duration=0,
            speed_based=False,
        )
    robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)

    # Get body part positions
    shoulder_id = 3001
    elbow_id = 3002
    wrist_id = 3003

    shoulder = env.GetAttr(shoulder_id)
    elbow = env.GetAttr(elbow_id)
    wrist = env.GetAttr(wrist_id)

    shoulder_position = shoulder.data["position"]
    elbow_position = elbow.data["position"]
    wrist_position = wrist.data["position"]

    # Add small random variations to make episodes diverse
    shoulder_noise = [random.uniform(-0.02, 0.02) for _ in range(3)]
    elbow_noise = [random.uniform(-0.02, 0.02) for _ in range(3)]

    shoulder_position = [p + n for p, n in zip(shoulder_position, shoulder_noise)]
    elbow_position = [p + n for p, n in zip(elbow_position, elbow_noise)]

    env.step()

    # Execution sequence for this episode
    # Phase 1: shoulder to elbow
    robot.IKTargetDoMove(
            position=[shoulder_position[0], shoulder_position[1]+0.1, shoulder_position[2]],
            duration=3,
            speed_based=False,
        )

    robot.IKTargetDoMove(
            position=[elbow_position[0], elbow_position[1]+0.1, elbow_position[2]],
            duration=3,
            speed_based=False,
        )
    for i in range(150):
        env.step()
        step_counter += 1
        if i % 10 == 0:  # Save every 10 steps
            save_step_data(step_counter, {'phase': 'shoulder_to_elbow', 'episode': episode})

    # Phase 2: elbow position
    for i in range(150):
        env.step()
        step_counter += 1
        if i % 10 == 0:  # Save every 10 steps
            save_step_data(step_counter, {'phase': 'elbow_position', 'episode': episode})

    # Phase 3: move above elbow
    robot.IKTargetDoMove(
            position=[elbow_position[0], elbow_position[1]+0.3, elbow_position[2]],
            duration=3,
            speed_based=False,
        )
    for i in range(150):
        env.step()
        step_counter += 1
        if i % 10 == 0:  # Save every 10 steps
            save_step_data(step_counter, {'phase': 'move_above_elbow', 'episode': episode})

    # Phase 4: elbow to shoulder
    robot.IKTargetDoMove(
            position=[shoulder_position[0], shoulder_position[1]+0.1, shoulder_position[2]],
            duration=3,
            speed_based=False,
        )
    for i in range(150):
        env.step()
        step_counter += 1
        if i % 10 == 0:  # Save every 10 steps
            save_step_data(step_counter, {'phase': 'elbow_to_shoulder', 'episode': episode})

    # Phase 5: final elbow position
    robot.IKTargetDoMove(
            position=[elbow_position[0], elbow_position[1]+0.1, elbow_position[2]],
            duration=3,
            speed_based=False,
        )
    for i in range(150):
        env.step()
        step_counter += 1
        if i % 10 == 0:  # Save every 10 steps
            save_step_data(step_counter, {'phase': 'final_elbow_position', 'episode': episode})

print(f"✅ Completed {EPISODE_NUMBER} episodes of rinse_upper data collection")

# Finalize data saving before closing
finalize_data_saving()

env.Pend()





