import numpy as np
from test_save_data_diffpolicy import init_data_saver, save_step_data, start_new_episode, finalize_data_saving
import pyrcareworld.attributes as attr

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld
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
# --------------------
# Config
# --------------------
ENABLE_DATA_SAVING = True
NUM_EPISODES = 5
NUM_WAYPOINTS = 50       # interpolate along +Y
DELTA_Y = 0.10           # meters
TASK_NAME = "bathing_rinse_upper"

# Ensure saver captures every step/waypoint
data_saver = init_data_saver(
    env,
    robot_id=315893,
    gripper_id=3158930,
    enabled=True,
    task_name=TASK_NAME,
    save_frequency=1,     # record every env.step exactly once per waypoint
    image_width=96,
    image_height=96
)

step_counter = 0
initialize_target = env.GetAttr(5678)
env.step()
initialize_position = initialize_target.data["position"]

# Build the fixed trajectory once (same for all episodes)
# Waypoints include start (0.0) and end (0.10) → 10 total
y_offsets = np.linspace(0.0, DELTA_Y, NUM_WAYPOINTS)
waypoints = [
    [initialize_position[0],
     initialize_position[1] + dy,
     initialize_position[2]]
    for dy in y_offsets
]

try:
    for ep in range(NUM_EPISODES):
        if ENABLE_DATA_SAVING:
            start_new_episode()

        # Reset to the same start pose each episode
        robot.IKTargetDoMove(position=initialize_position, duration=0, speed_based=False)
        robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        env.step(5)  # settle a few ticks

        # Follow the same interpolated Y-trajectory by teleporting to each waypoint
        for wp_idx, p in enumerate(waypoints):
            # Teleport move (duration=0)
            robot.IKTargetDoMove(position=p, duration=0, speed_based=False)
            robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)

            # Advance sim once to apply state, then record
            env.step()
            step_counter += 1

            if ENABLE_DATA_SAVING:
                save_step_data(
                    step_counter,
                    {'episode': ep, 'phase': 'linear_y_0.1m', 'waypoint_idx': wp_idx}
                )

    if ENABLE_DATA_SAVING:
        finalize_data_saving()

finally:
    env.Pend()
