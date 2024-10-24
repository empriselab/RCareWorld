from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

# Initialize the environment
env = RCareWorld()

# Instantiate the shadow hand object with a controller attribute
shadow = env.InstanceObject("shadowhand", attr_type=attr.ControllerAttr)

# Set the position of the shadow hand
shadow.SetPosition([0, 1, 0])

# Add a 6DOF root to the shadow hand
root = shadow.AddRoot6DOF()

# Perform a simulation step to update the environment
env.step()

# Set joint stiffness and damping for the root
root.SetJointStiffness([100] * 6)
root.SetJointDamping([50] * 6)

# Function to set joint positions with a delay between each step
def set_joint_positions_with_delay(root, positions, delay_steps):
    for index, position in positions:
        root.SetIndexJointPosition(index, position)
        env.step(delay_steps)

# Define joint positions and delays
joint_positions = [
    (0, 0.5),
    (1, 0.5),
    (2, 0.5),
    (3, 45),
    (4, 45),
    (5, 45)
]
delay_steps = 50

# Set the joint positions with delays
set_joint_positions_with_delay(root, joint_positions, delay_steps)

# Close the environment
env.Pend()
env.close()
