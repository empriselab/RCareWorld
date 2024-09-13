import os
import sys
import random
import numpy as np
try:
    import gymnasium as gym
except ImportError:
    print("This feature requires gymnasium, please install with `pip install gymnasium`")
    raise
from gymnasium import spaces
import pyrcareworld.attributes as attr
from pyrcareworld.envs.base_env import RCareWorld

# Import PPO and other utilities from stable_baselines3
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor

class ReachTargetEnv(gym.Env):
    def __init__(self):
        super(ReachTargetEnv, self).__init__()

        # Initialize the environment
        self.env = RCareWorld(assets=["kinova_gen3_robotiq85", "GameObject_Box"], executable_file="../executable/Player/Player.x86_64")
        self.box = self.env.InstanceObject(name="GameObject_Box", id=111111, attr_type=attr.GameObjectAttr)

        self.init_pose = [0.2, 0.5, -0.5]

        self.box.SetTransform(
            position=self.init_pose,
            scale=[0.1, 0.1, 0.1],
        )

        # Initialize the robot
        self.robot = self.env.InstanceObject(name="kinova_gen3_robotiq85", id=123456, attr_type=attr.ControllerAttr)
        self.robot.SetPosition([0,0,0])
        self.robot.IKTargetDoMove(position=self.init_pose, duration=0, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        self.robot.WaitDo()
        self.robot.IKTargetDoComplete()

        self.env.step()
        self.env.ViewLookAt(self.robot.data["position"])
        self.env.step()

        self.gripper = self.env.GetAttr(1234560)
        self.env.step()
        print(self.gripper.data)

        # Define action and observation space
        self.action_space = spaces.Box(low=-0.1, high=0.1, shape=(3,), dtype=np.float32)  # 3D movements in XYZ
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(6,), dtype=np.float32)  # Robot and target position

        # Initialize target position
        self.target_position = np.array([random.uniform(0.3, 0.5), 0.2, random.uniform(-0.55, -0.45)])
        self.robot_position = np.array([0.2, 0.2, -0.5])

    def reset(self, seed=None, options=None):
        # Handle the seed if provided
        if seed is not None:
            self.np_random, seed = gym.utils.seeding.np_random(seed)

        # Randomize the target position
        self.target_position = np.array([random.uniform(0.3, 0.5), 0.2, random.uniform(-0.55, -0.45)])

        self.box.SetTransform(
            position=self.target_position,
            scale=[0.1, 0.1, 0.1],
        )
        self.env.step()

        # Move the robot to the initial observation position
        self.robot.IKTargetDoMove(position=self.init_pose, duration=0, speed_based=False)
        self.robot.WaitDo()
        self.robot.IKTargetDoComplete()
        self.env.step()

        # Update the robot's internal position state
        self.robot_position = self.init_pose

        # Return only the observation, even if `gymnasium` expects to return (observation, info)
        observation = np.concatenate([self.robot_position, self.target_position])
        print("++++++++++++++")
        print("resetting")
        return observation, None  # If using gymnasium, omit the info

    def step(self, action):
        # Apply the action to the robot position
        self.robot_position += action
        self.robot.IKTargetDoMove(position=self.robot_position.tolist(), duration=0.5, speed_based=False)
        self.robot.WaitDo()
        # self.robot.IKTargetDoComplete()
        self.env.step(100)

        # Calculate the distance to the target
        self.robot_position = self.gripper.data["positions"][-1]
        print(self.robot_position)
        distance_to_target = np.linalg.norm(self.robot_position - self.target_position)

        # Define the reward (negative distance to the target)
        reward = -distance_to_target

        # Check if the target is reached
        done = distance_to_target < 0.1  # Considered success if within 10cm of the target

        # Prepare the next observation
        observation = np.concatenate([self.robot_position, self.target_position])

        return observation, reward, done, {}, {}

    def render(self, mode='human'):
        pass

    def close(self):
        self.env.close()
    

if __name__ == "__main__":

    # Initialize the environment
    env = ReachTargetEnv()

    # Wrap the environment for monitoring and vectorization
    env = Monitor(env)
    env = DummyVecEnv([lambda: env])

    # Create a PPO agent
    model = PPO("MlpPolicy", env, verbose=1, device='cuda')  # Specify 'cuda' to use GPU

    # Train the agent
    model.learn(total_timesteps=10000)

    # Save the trained agent
    model.save("reach_target_ppo")

    # Optionally, load and evaluate the agent
    model = PPO.load("reach_target_ppo")
    obs = env.reset()
    for _ in range(1000):
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        print(rewards)
        # if done:
        #     obs = env.reset()
        obs = env.reset()

    env.close()
