import os
import sys
import random
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld
from save_data_diffusion import init_data_saver, save_step_data, start_new_episode, finalize_data_saving

# Enable data saving (set to False to disable)
ENABLE_DATA_SAVING = True

offset = 0.05  # offset to avoid collision with the arm

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

# # Set high frequency time step for smooth simulation (0.01s = 100Hz)
# env.SetTimeStep(0.01)

# Create an instance of the Franka Panda robot and set its IK target offset
robot = env.GetAttr(315893)

env.step()

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(3158930)
gripper.GripperOpen()

# Number of episodes to collect (default: 20)
EPISODE_NUMBER = 5  # Test with 1 episode first

# Initialize data saver for bathing dry task (save every 10 steps)
data_saver = init_data_saver(env, robot_id=315893, gripper_id=3158930,
                             enabled=ENABLE_DATA_SAVING, task_name="bathing_simple_line", save_frequency=5)

print(f"🚀 Starting data collection for {EPISODE_NUMBER} episodes...")

# Execute multiple episodes
for episode in range(EPISODE_NUMBER):
    print(f"\n🎬 ====== Episode {episode + 1}/{EPISODE_NUMBER} Started ======")

    # Start new episode
    if ENABLE_DATA_SAVING:
        start_new_episode()
        print(f"💾 [Episode {episode + 1}] New episode started for data saving")

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

    

    # only randomize x and z for shoulder and elbow
    # shoulder_noise = [random.uniform(-0.02, 0.02), 0.0, random.uniform(-0.02, 0.02)]
    # elbow_noise = [random.uniform(-0.02, 0.02), 0.0, random.uniform(-0.02, 0.02)]
    # pad_dry_wp_noise = [random.uniform(-0.02, 0.02) for _ in range(3)]

    # shoulder_position = [p + n for p, n in zip(shoulder_position, shoulder_noise)]
    # elbow_position = [p + n for p, n in zip(elbow_position, elbow_noise)]
    # pad_dry_wp_position = [p + n for p, n in zip(pad_dry_wp_position, pad_dry_wp_noise)]

    env.step()
    print(f"🤖 [Episode {episode + 1}] Robot initialized, starting movements...")

    # move to shoulder
    print(f"🎯 [Episode {episode + 1}] Phase 1: Moving to shoulder position")
    robot.IKTargetDoMove(
            position=[initialize_position[0], initialize_position[1]+0.05, initialize_position[2]],
            duration=0.5,
            speed_based=False,
        )

    for i in range(100):
        env.step()
        step_counter += 1
        save_step_data(step_counter, {'phase': 'test', 'episode': episode})
        print(f"💾 [Episode {episode + 1}] Step {step_counter}: Saved 'move simple line' data")



    print(f"🏁 [Episode {episode + 1}] Completed! Total steps saved: {step_counter}")
    print(f"🎬 ====== Episode {episode + 1}/{EPISODE_NUMBER} Finished ======\n")

print(f"\n🎉 ✅ Completed ALL {EPISODE_NUMBER} episodes of dry_upper data collection! 🎉")

# Finalize data saving before closing
finalize_data_saving()

env.Pend()





