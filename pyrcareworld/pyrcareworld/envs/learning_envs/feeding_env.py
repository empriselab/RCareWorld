from pyrcareworld.envs import RCareWorldGymWrapper
from gym import spaces
from gym.utils import seeding
import numpy as np
import pybullet as p
import math


class FeedingEnv(RCareWorldGymWrapper):
    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(
        self,
        assets=[],
        load_food=True,
        tolerance=0.05,
        reward_type="sparse",
        neck_rotation_min=-15,
        neck_rotation_max=15,
        executable_file=None,
        scene_file: str = None,
        custom_channels: list = [],
        food_tolerance=0.05,
    ):
        super().__init__(
            executable_file=executable_file,
            scene_file=scene_file,
            custom_channels=custom_channels,
            assets=assets,
        )

        self.load_food = load_food

        self.robot = self.create_robot(315893, [3158930], "kinova_gen3_7dof")
        self.init_pose_obj = self.create_object(12344, "Ini", True)
        ini_world_pose = self.init_pose_obj.getPosition()
        self.eef_orn = p.getQuaternionFromEuler([0, -math.pi / 2.0, 0.0])
        self.robot.moveTo(ini_world_pose, self.eef_orn)
        self.robot.closeGripper()
        for i in range(40):
            self._step()

        if self.load_food:
            self._load_food()

        self.spoon = self.create_object(114514, "Spoon", True)
        self.human = self.create_human(2322, "man", True)
        self.neck_rotation_min = neck_rotation_min
        self.neck_rotation_max = neck_rotation_max
        for i in range(10):
            self._step()

        self.tolerance = tolerance
        self.food_tolerance = food_tolerance
        self.reward_type = reward_type

        self.seed()
        self.target = self.create_object(12345, "Target", True)
        self.target_pos = self.target.getPosition()

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

        self.action_space = spaces.Box(low=-1, high=1, shape=(3,), dtype=np.float32)

        self._step()

    def demo_env(self, user_input=False, record=False):
        taget_pos = self.init_pose_obj.getPosition()
        print(taget_pos)
        self.robot.directlyMoveTo(taget_pos, self.eef_orn)
        self._step()
        self.human.setJointRotationByNameDirectly("Neck", [10, 0, 0])

    def _load_food(self):
        self.food = self.create_object(19024, "food", False)
        self.food.load(position=[0.4105, 0.9996, -0.1148])
        for i in range(5):
            self._step()
        # for i in range(500):
        #     self._step()

    def get_obs(self):
        kinova_obs = np.array(self.robot.getGripperPosition())
        spoon_obs = np.array(self.spoon.getPosition())
        food_obs = np.array(self.food.getPosition())
        human_obs = np.array(self.human.getJointRotationByName("Neck"))
        target_obs = np.array(self.target.getPosition())
        # return human_obs
        obs = np.concatenate((kinova_obs, spoon_obs, food_obs, human_obs, target_obs))
        achieved_goal = food_obs.copy()
        return {
            "observation": obs.copy(),
            "achieved_goal": achieved_goal.copy(),
            "desired_goal": np.array(self.target_pos).copy(),
        }

    def step(self, action: np.ndarray):
        a = action.copy()
        pos_ctrl = a * 0.03
        current_pos = self.robot.getGripperPosition()
        next_pos = current_pos + pos_ctrl
        self.robot.moveTo(next_pos, self.eef_orn)
        self.t += 1

        obs = self.get_obs()
        done = False
        info = {"is_success": self._check_success(obs)}
        info["food_position"] = np.array(self.food.getPosition())
        info["spoon_position"] = np.array(self.spoon.getPosition())
        reward = self.compute_reward(obs["achieved_goal"], obs["desired_goal"], info)

        food_fail = self._check_food_fall(info)
        if food_fail:
            done = True
            obs = self.reset()

        return obs, reward, done, info

    def _check_success(self, obs):
        achieved_goal = obs["achieved_goal"]
        desired_goal = obs["desired_goal"]
        distance = self._compute_goal_distance(achieved_goal, desired_goal)
        return (distance < self.tolerance).astype(np.float32)

    def _check_food_fall(self, info):
        food_spoon_distance = self._compute_goal_distance(
            info["food_position"], info["spoon_position"]
        )
        return float(food_spoon_distance) > self.food_tolerance

    def _compute_goal_distance(self, goal_a, goal_b):
        assert goal_a.shape == goal_b.shape
        return np.linalg.norm(goal_a - goal_b, axis=-1)

    def compute_reward(
        self, achieved_goal: np.ndarray, desired_goal: np.ndarray, info: dict
    ):
        distance = self._compute_goal_distance(achieved_goal, desired_goal)
        food_reward = 2
        if self.reward_type == "sparse":
            return -(distance > self.tolerance).astype(np.float32) + food_reward
        else:
            return -distance + food_reward

    def _randomize_neck(self):
        random_neck = np.random.uniform(self.neck_rotation_min, self.neck_rotation_max)
        random_neck = np.array([random_neck, 0, 0])
        return random_neck

    def reset(self):
        super().reset()
        self.t = 0
        self.robot.directlyMoveTo(self.init_pose_obj.getPosition(), self.eef_orn)
        for i in range(40):
            self._step()
        neck_pos = self._randomize_neck()
        self.human.setJointRotationByNameDirectly("Neck", neck_pos)
        self.target_pos = self.target.getPosition()
        self.food.destroy()
        self.food.load(position=[0.4105, 0.9996, -0.1148])
        for i in range(5):
            self._step()
        return self.get_obs()


if __name__ == "__main__":
    env = FeedingEnv()
    for i in range(10000):
        env.reset()
