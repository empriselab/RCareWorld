from pyrcareworld.envs import RCareWorldGymWrapper
from gym import spaces
from gym.utils import seeding
import numpy as np
import pybullet as p
import math


class YourLearningEnv(RCareWorldGymWrapper):
    def __init__(
        self,
        max_steps=100,
        tolerance=0.1,
        init_random=False,
        robot_init_random_range=0.03,
        render=False,
        executable_file=None,
        scene_file: str = None,
        custom_channels: list = [],
        assets: list = [],
        **kwargs
    ):
        super().__init__(
            executable_file=executable_file,
            scene_file=scene_file,
            custom_channels=custom_channels,
            assets=assets,
            **kwargs,
        )
        self.max_steps = max_steps
        self.tolerance = tolerance
        self.init_random = init_random
        self.robot_init_random_range = robot_init_random_range
        self.robot_init_random_range_min = np.array(
            [-self.robot_init_random_range, 0, -self.robot_init_random_range]
        )
        self.robot_init_random_range_max = np.array(
            [self.robot_init_random_range, 0, self.robot_init_random_range]
        )
        self._render = render

        self.robot = self.create_robot(35987, [359870], "kinova_gen3_7dof")

        self.init_joint_positions = np.array([0] * 7)
        self.eef_euler = np.array([math.pi / 2, 0, -math.pi / 2])
        self.eef_orn = p.getQuaternionFromEuler([math.pi / 2, 0, -math.pi / 2])

        self.t = 0
        self.seed()
        self.action_space = spaces.Box(low=-1, high=1, shape=(3,), dtype=np.float32)

        self.robot = self.get_robot(35987)

        self.target = self.create_object(197454, "Target", True)
        self.hand = self.create_object(197453, "Hand", True)

        obs = self.get_obs()

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=obs.shape, dtype=np.float32
        )

    def step(self, action: np.ndarray):
        a = action.copy()
        delta_pos = a * 0.05
        curr_pos = self.get_eef_position()
        target_pos = curr_pos + delta_pos
        self.robot.moveTo(target_pos, self.eef_orn)
        self.t += 1
        obs = self.get_obs()
        done = False
        success = self._check_success()
        reward = self._compute_reward()
        info = {"is_success": success}
        if self.t == self.max_steps or success:
            done = True

        return obs, reward, done, info

    def reset(self):
        self.robot.reset()
        self.robot.setJointPositionsDirectly(self.init_joint_positions)
        self._reset_human()
        self.t = 0
        # self.teaching_seq_id = 0

        hand_position = self.get_hand_position()

        if self.init_random:
            hand_position += self.np_random.uniform(
                low=self.robot_init_random_range_min,
                high=self.robot_init_random_range_max,
            )

        self.robot.directlyMoveTo(hand_position)
        return self.get_obs()

    def render(self, mode="human"):
        self._step()

    def seed(self, seed=1234):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_obs(self):
        self._step()
        limb_tool_position = self.get_eef_position()
        limb_tool_velocity = self.get_eef_velocity()
        robot_obs = np.concatenate((limb_tool_position, limb_tool_velocity))

        hand_position = self.get_hand_position()
        target_position = self.get_target_position()
        human_obs = np.concatenate((hand_position, target_position))

        return np.concatenate((robot_obs, human_obs)).copy()

    def get_target_position(self):
        return np.array(self.target.getPosition())

    def get_hand_position(self):
        return np.array(self.hand.getPosition())

    def get_eef_position(self):
        return np.array(self.robot.getGripperPosition())

    def get_eef_velocity(self):
        return np.array(self.robot.getGripperVelocity())

    def _reset_human(self):
        self.instance_channel.set_action(
            "SetJointPositionDirectly", id=36000, joint_positions=[0, 0, 0]
        )
        # wait until the limb falls down
        for i in range(150):
            self._step()

    def _check_success(self):
        hand_pos = self.get_hand_position()
        target_pos = self.get_target_position()
        distance = self._compute_distance(hand_pos, target_pos)
        return distance < self.tolerance

    def _compute_distance(self, goal_a, goal_b):
        assert goal_a.shape == goal_b.shape
        return np.linalg.norm(goal_a - goal_b, axis=-1)

    def _compute_reward(self):
        hand_pos = self.get_hand_position()
        target_pos = self.get_target_position()
        eef_pos = self.get_eef_position()
        eef_hand_dis = self._compute_distance(eef_pos, hand_pos)
        hand_target_dis = self._compute_distance(hand_pos, target_pos)

        # set weight for hand_target_distance and eef_hand_distance
        return -2 * hand_target_dis - eef_hand_dis


if __name__ == "__main__":
    env = YourLearningEnv()
    while True:
        env.get_obs()
        env.reset()
        env.robot.moveTo(env.hand.getPosition())
        for i in range(100):
            env._step()
