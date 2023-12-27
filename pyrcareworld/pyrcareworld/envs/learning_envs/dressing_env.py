from pyrcareworld.envs import RCareWorldGymWrapper
from gym import spaces
from gym.utils import seeding
import numpy as np
import pybullet as p
import math


class DressingEnv(RCareWorldGymWrapper):
    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(
        self,
        assets=["pants", "kinova_gen3_robotiq85_dressing"],
        tolerance=0.05,
        executable_file=None,
        scene_file: str = None,
        custom_channels: list = [],
        max_episode_length = 100,
    ):
        super().__init__(
            executable_file=executable_file,
            scene_file=scene_file,
            custom_channels=custom_channels,
            assets=assets,
        )

        for i in range(40):
            self._step()

        self.robot = self.create_robot(315893, [3158930], "kinova_gen3_7dof-dressing")
        self.robot.load()
        self.init_pose_obj = self.create_object(12344, "IniObject", True)
        self.human = self.create_human(85042, "male1_c6-c7", True)
        self.pants = self.create_object(2332, "pants", False)
        self.target = self.create_object(22344, "target", True)
        self._step()

        ini_world_pose = self.init_pose_obj.getPosition()
        self.eef_orn = p.getQuaternionFromEuler([math.pi / 2.0, -math.pi / 2.0, 0.0])
        self._step()
        self.robot.directlyMoveTo(ini_world_pose, self.eef_orn)
        for i in range(20):
            self._step()
        # self.pants.load(position=[0.85, -0.12, -0.44], rotation=[-180, 85, -0.2])
        self.target_pos = self.target.getPosition()
        self.action_space = spaces.Box(low=-1, high=1, shape=(3,), dtype=np.float32)
        obs = self.get_obs()
        self.observation_space = spaces.Dict(
            {
                "observation": spaces.Box(
                    -np.inf, np.inf, shape=obs["observation"].shape, dtype=np.float32
                ),
                "desired_goal": spaces.Box(
                    -np.inf, np.inf, shape=obs["desired_goal"].shape, dtype=np.float32
                ),
                "achieved_goal": spaces.Box(
                    -np.inf, np.inf, shape=obs["achieved_goal"].shape, dtype=np.float32
                ),
            }
        )
        self.max_episode_length = max_episode_length
        self.tolerance = 0.05

    def demo_env(self, user_input=False, record=False):
        for i in range(10000):
            ini_world_pose = self.init_pose_obj.getPosition()
            self.robot.directlyMoveTo(ini_world_pose, self.eef_orn)
            self._step()

    def get_obs(self):
        kinova_obs = np.array(self.robot.getGripperPosition())
        grasp_point_obs = np.array(self.robot.getGripperGraspPointPosition())
        target_obs = np.array(self.target.getPosition())
        pants_obs = np.array(self.pants.getPosition())
        human_obs_lower_leg = np.array(
            self.human.getJointPositionByName("RightLowerLeg")
        )
        human_obs_upper_leg = np.array(
            self.human.getJointPositionByName("RightUpperLeg")
        )
        obs = np.concatenate(
            (
                kinova_obs,
                grasp_point_obs,
                pants_obs,
                human_obs_lower_leg,
                human_obs_upper_leg,
                target_obs,
            )
        )
        achieved_goal = grasp_point_obs.copy()
        return {
            "observation": obs.copy(),
            "achieved_goal": achieved_goal.copy(),
            "desired_goal": np.array(self.target_pos).copy(),
        }

    def step(self, action: np.ndarray):
        a = action.copy()
        pos_ctrl = a * 0.03
        current_pos = self.robot.getGripperGraspPointPosition()
        next_pos = current_pos + pos_ctrl
        self.robot.moveTo(next_pos, self.eef_orn)
        self.t += 1

        obs = self.get_obs()
        done = False
        success = self._check_success(obs)
        info = {"is_success": success}
        reward = self.compute_reward(obs["achieved_goal"], obs["desired_goal"], info)
        if self.t == self.max_episode_length or success:
            done = True
        return obs, reward, done, info

    def _check_success(self, obs):
        achieved_goal = obs["achieved_goal"]
        desired_goal = obs["desired_goal"]
        distance = self._compute_goal_distance(achieved_goal, desired_goal)
        return (distance < self.tolerance).astype(np.float32)

    def _compute_goal_distance(self, goal_a, goal_b):
        assert goal_a.shape == goal_b.shape
        return np.linalg.norm(goal_a - goal_b, axis=-1)

    def compute_reward(self, achieved_goal: np.ndarray, desired_goal: np.ndarray, info):
        distance = self._compute_goal_distance(achieved_goal, desired_goal)
        return -distance

    def reset(self):
        super().reset()
        self.t = 0
        # reset robot
        self.robot.destroy()
        self.robot.load()
        self.robot.directlyMoveTo(self.init_pose_obj.getPosition(), self.eef_orn)
        # reset pants
        self.pants.setActive(False)
        self._step()
        self.pants.setActive(True)
        self.pants.setTransform(
            position=[0.85, -0.12, -0.44], rotation=[-180, 85, -0.2]
        )
        # self.pants.destroy()
        # self.pants.load(position=[0.85, -0.12, -0.44], rotation=[-180, 85, -0.2])
        # reset target
        # self.target.setTransform(position=[0.23, 0.0, -0.45])
        deviation = 0.02
        target_position = np.array([0.31, 0.0, -0.45])
        offset_x = np.random.uniform(-deviation, deviation)
        offset_z = np.random.uniform(-deviation, deviation)
        offsets = np.array([offset_x, 0.0, offset_z])
        randomized_position = target_position + offsets
        self.target.setTransform(position=randomized_position.tolist())
        self._step()
        return self.get_obs()


if __name__ == "__main__":
    env = DressingEnv(executable_file="@Editor")
    for i in range(10000):
        print(env.reset())
        print(env.instance_channel.data[3158930])
