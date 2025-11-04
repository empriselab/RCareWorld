import os
import sys
import random
import numpy as np
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld
from save_data_diffusion import init_data_saver, save_step_data, start_new_episode, finalize_data_saving

# Enable data saving (set to False to disable)
ENABLE_DATA_SAVING = True

offset = 0.1  # offset to avoid collision with the arm (unused below; keep if needed)

# Enable SSH remote connection (set to True to use remote Unity)
USE_REMOTE = False

# Configure environment based on connection mode
if USE_REMOTE:
    env = RCareWorld(bind_address="0.0.0.0", remote_mode=True, port=5004)
    print("[Remote Mode] Waiting for Unity connection on 0.0.0.0:5004")
else:
    env = RCareWorld()

# Create an instance of the Franka Panda robot
robot = env.GetAttr(315893)
env.step()

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(3158930)
gripper.GripperOpen()

# Number of episodes to collect
EPISODE_NUMBER = 3

# Initialize data saver (save every 5 steps)
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

    # Teleport to the initial pose and set a fixed tool orientation
    robot.IKTargetDoMove(position=initialize_position, duration=0, speed_based=False)
    robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
    env.step()
    print(f"🤖 [Episode {episode + 1}] Robot initialized, starting movements...")

    # ------- Interpolate 100 absolute waypoints along a straight line -------
    # Target pose: +0.3 m on X (keep Y,Z same). Modify as needed.
    target_position = [initialize_position[0] + 0.3,
                       initialize_position[1],
                       initialize_position[2]]

    # Generate 100 waypoints including the end point (shape: (100, 3))
    waypoints = np.linspace(initialize_position, target_position, num=100, endpoint=True)

    print(f"🎯 [Episode {episode + 1}] Interpolating 100 waypoints from {initialize_position} -> {target_position}")

    # Execute waypoints (skip index 0 since we're already at initialize_position)
    for i in range(1, len(waypoints)):
        wp = waypoints[i].tolist()

        # Teleport move to absolute waypoint
        robot.IKTargetDoMove(position=wp, duration=0, speed_based=False)
        robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)

        # Advance sim one tick so the motion applies and sensors update
        env.step()

        # Save data once per step; step_counter advances each waypoint
        step_counter += 1
        save_step_data(step_counter, {'phase': 'interp_line', 'episode': episode, 'wp_idx': i})

        if i % 10 == 0 or i == len(waypoints) - 1:
            print(f"  • Waypoint {i}/99 at {wp}")

    print(f"🏁 [Episode {episode + 1}] Completed! Total steps saved: {step_counter}")
    print(f"🎬 ====== Episode {episode + 1}/{EPISODE_NUMBER} Finished ======\n")

print(f"\n🎉 ✅ Completed ALL {EPISODE_NUMBER} episodes of simple-line data collection! 🎉")

# Finalize data saving before closing
finalize_data_saving()

env.Pend()
