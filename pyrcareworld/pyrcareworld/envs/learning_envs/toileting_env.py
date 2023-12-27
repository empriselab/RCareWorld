from pyrcareworld.envs import RCareWorldGymWrapper
from gym import spaces
from gym.utils import seeding
import numpy as np
import pybullet as p
import math


class StretchToiletEnv(RCareWorldGymWrapper):
    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(
        self,
        max_step,
        # asset_bundle_file,
        toilet_pose_min=[-0.05, -0.05, 0.9, 0, -80, 0],
        toilet_pose_max=[0.05, 0.05, 1.1, 0, -100, 0],
        success_joint_position=40,
        relative_joint_position_reward=False,
        executable_file=None,
    ):
        """
        relative_joint_position_reward: If set to true, reward computation will be based on the
            relative joint position change. Under this setting, if Stretch makes the toilet open
            smaller in a step, it will get a negative reward. And this will promise the episodic
            reward is the final toilet open angle.
        """
        super().__init__(
            executable_file=executable_file,
            camera_channel=True,
            articulation_channel=True,
            game_object_channel=True,
        )
        self.max_step = max_step
        # self.asset_bundle = asset_bundle_file
        self.toilet_pose_min = toilet_pose_min
        self.toilet_pose_max = toilet_pose_max
        self.success_joint_position = success_joint_position
        self.relative_joint_position_reward = relative_joint_position_reward

        self.t = 0
        self.last_toilet_open_angle = 0

        self.robot = self.create_robot()
        self.loaded = False
        self.seed()
        self._load_toilet()

        self.action_space = spaces.Box(low=-1, high=1, shape=(3,), dtype=np.float32)
        obs = self._get_obs()
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=obs.shape, dtype=np.float32
        )

    def step(self, action: np.ndarray):
        pos_ctrl = action.copy()
        curr_pos = self._get_eef_position()
        pos_ctrl = curr_pos + pos_ctrl * 0.05
        joint_positions = self.ik_controller.calculate_ik(pos_ctrl)
        self._set_stretch(joint_positions)

        self.t += 1
        done = False
        obs = self._get_obs()
        reward = self._compute_reward(obs)
        info = {"is_success": self._check_success(obs)}
        self.last_toilet_open_angle = float(obs[-1]) * -1

        if self.t == self.max_step:
            obs = self.reset()
            done = True

        return obs, reward, done, info

    def reset(self):
        self.env.reset()
        self.t = 0
        self.last_toilet_open_angle = 0
        self._destroy_toilet()
        self.ik_controller.reset()
        self._reset_stretch()
        self._load_toilet()

        toilet_target_position = self._get_toilet_target_position()
        joint_positions = self.ik_controller.calculate_ik_recursive(
            toilet_target_position
        )
        self._set_stretch_directly(joint_positions)

        return self._get_obs()

    def seed(self, seed=1234):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def render(self, mode="human"):
        self.camera_channel.set_action("GetImages", rendering_params=[[0, 512, 512]])
        self._step()
        img = self.camera_channel.images.pop(0)

        return img

    def heuristic(self):
        self.ik_controller.reset()
        position = self._get_target_position()
        joint_positions = self.ik_controller.calculate_ik_recursive(position)
        self._set_stretch_directly(joint_positions)

    def _get_obs(self):
        stretch_obs = self._get_eef_position()
        toilet_base = self._get_toilet_base_position()
        toilet_revolute_joint = self._get_toilet_revolute_joint_position()
        toilet_push_point = self._get_toilet_target_position()
        toilet_joint_position = self._get_toilet_joint_position()

        obs = np.concatenate(
            (
                stretch_obs,
                toilet_base,
                toilet_revolute_joint,
                toilet_push_point,
                [toilet_joint_position],
            )
        )

        return obs.copy()

    def _compute_reward(self, obs: np.ndarray):
        if not self.relative_joint_position_reward:
            return float(obs[-1]) / 10 * -1
        else:
            return -1 * float(obs[-1]) - self.last_toilet_open_angle

    def _check_success(self, obs):
        return float(float(obs[-1]) * -1 > self.success_joint_position)

    def _load_toilet(self, position=None, rotation=None):
        random_pose = self.np_random.uniform(self.toilet_pose_min, self.toilet_pose_max)
        if position is None:
            position = list(random_pose[0:3])
        if rotation is None:
            rotation = list(random_pose[3:6])
        self.asset_channel.set_action(
            "InstanceObject",
            # filename=self.asset_bundle,
            name="Toilet",
            id=123,
            # position=position,
            # rotation=rotation
        )
        self.articulation_channel.set_action(
            "SetTransform",
            id=123,
            position=[0, 0, 0],
            rotation=[0, -90, 0],
        )
        self._step()
        self.loaded = True

    def _destroy_toilet(self):
        self.articulation_channel.set_action("Destroy", id=1)
        self._step()
        self.loaded = False

    def _reset_stretch(self):
        self._set_stretch_directly([0] * 10)

    def _get_target_position(self):
        return np.array(self.game_object_channel.data[0]["position"])

    def _get_toilet_base_position(self):
        assert self.loaded is True
        return np.array(self.articulation_channel.data[1]["positions"][0])

    def _get_toilet_revolute_joint_position(self):
        assert self.loaded is True
        return np.array(self.articulation_channel.data[1]["positions"][1])

    def _get_toilet_target_position(self):
        assert self.loaded is True
        return np.array(self.articulation_channel.data[1]["positions"][2])

    def _get_toilet_joint_position(self):
        assert self.loaded is True
        return self.articulation_channel.data[1]["joint_positions"][0]

    def _get_eef_position(self):
        return np.array(self.articulation_channel.data[0]["positions"][30])

    def _set_stretch(self, joint_positions):
        self.articulation_channel.set_action(
            "SetJointPosition", index=0, joint_positions=list(joint_positions)
        )
        self._step()

    def _set_stretch_directly(self, joint_positions):
        self.articulation_channel.set_action(
            "SetJointPositionDirectly", index=0, joint_positions=list(joint_positions)
        )
        self._step()
