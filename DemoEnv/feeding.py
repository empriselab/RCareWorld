from pyrfuniverse.envs import RFUniverseBaseEnv
from pyrfuniverse.envs import RFUniverseGymGoalWrapper
from pyrfuniverse.utils.kinova_controller import RFUniverseKinovaController
from pyrfuniverse.utils.interpolate_utils import sine_interpolate
from pyrfuniverse.utils.camera_utils import save_image
from gym import spaces
from gym.utils import seeding
import numpy as np
import pybullet as p
import math


class KinovaSpoonEnv(RFUniverseGymGoalWrapper):
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(
            self,
            asset_bundle_file,
            load_food=False,
            tolerance=0.05,
            reward_type='sparse',
            neck_rotation_min=0,
            neck_rotation_max=15,
            head_rotation_min=-10,
            head_rotation_max=10,
            executable_file=None
    ):
        super().__init__(
            executable_file=executable_file,
            camera_channel_id="f9576dd0-7440-11ec-959e-18c04d443e7d",
            rigidbody_channel_id="f9576dd3-7440-11ec-959e-18c04d443e7d",
            articulation_channel_id="f9576dd2-7440-11ec-959e-18c04d443e7d",
            game_object_channel_id="f9576dd1-7440-11ec-959e-18c04d443e7d",
        )
        self.asset_bundle_file = asset_bundle_file
        self.load_food = load_food
        self.tolerance = tolerance
        self.food_tolerance = self.tolerance
        self.reward_type = reward_type
        self.neck_head_rotation_min = np.array([neck_rotation_min, head_rotation_min])
        self.neck_head_rotation_max = np.array([neck_rotation_max, head_rotation_max])

        if self.load_food:
            self._load_food()
        self.seed()
        self.ik_controller = RFUniverseKinovaController(
            robot_urdf='/home/haoyuan/workspace/rfuniverse/rfuniverse/external_assets/urdf/urdf/kinova_gen3/GEN3_URDF_V12.urdf'
        )
        self.t = 0
        self.eef_orn = p.getQuaternionFromEuler([math.pi / 2., -math.pi / 2., 0.])
        self.init_position = np.array([-0.3, 0.5, 0.3])
        self.init_joint_positions = self.ik_controller.calculate_ik_recursive(
            self.init_position,
            self.eef_orn
        )
        self.neck_head_rot = np.array([0, 0])
        self.goal = self._get_target_position()

        self.action_space = spaces.Box(
            low=-1, high=1, shape=(3,), dtype=np.float32
        )
        obs = self._get_obs()
        self.observation_space = spaces.Dict({
            'observation': spaces.Box(-np.inf, np.inf, shape=obs['observation'].shape, dtype=np.float32),
            'desired_goal': spaces.Box(-np.inf, np.inf, shape=obs['desired_goal'].shape, dtype=np.float32),
            'achieved_goal': spaces.Box(-np.inf, np.inf, shape=obs['achieved_goal'].shape, dtype=np.float32)
        })

        # Re-organize camera
        self.camera_channel.set_action(
            'ResetCamera',
            index=0,
            position=[-0.172999993, 0.726000011, 1.023],
            rotation=[24.2765617, 148.114105, -9.36595313e-07]
        )
        self._step()

    def step(self, action: np.ndarray):
        a = action.copy()
        pos_ctrl = a * 0.03
        curr_pos = self._get_eef_position()
        pos_ctrl = curr_pos + pos_ctrl

        joint_positions = self.ik_controller.calculate_ik(
            pos_ctrl,
            eef_orn=self.eef_orn
        )
        self._set_kinova_joints(joint_positions)
        self.t += 1

        obs = self._get_obs()
        done = False
        info = {
            'is_success': self._check_success(obs)
        }
        if self.load_food:
            info['food_position'] = self._get_food_position()
            info['spoon_position'] = self._get_spoon_position()
        reward = self.compute_reward(obs['achieved_goal'], obs['desired_goal'], info)

        if self.load_food:
            food_fall = self._check_food_fall(info)
            if food_fall:
                done = True
                obs = self.reset()

        return obs, reward, done, info

    def reset(self):
        super().reset()
        self.env.reset()
        self.t = 0
        self.ik_controller.reset()

        # Reset Kinova
        self._set_kinova_joints_directly(self.init_joint_positions)

        # Reset food
        if self.load_food:
            self._destroy_food()
            self._load_food()

        # Randomize human neck and head
        self.neck_head_rot = self._randomize_neck_head()
        self._set_human_neck_head()
        self.goal = self._get_target_position()

        return self._get_obs()

    def seed(self, seed=1234):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def render(self, mode='human'):
        self.camera_channel.set_action(
            'GetImages',
            rendering_params=[[0, 512, 512]]
        )
        self._step()
        img = self.camera_channel.images.pop(0)

        return img

    def compute_reward(self, achieved_goal: np.ndarray, desired_goal: np.ndarray, info: dict):
        distance = self._compute_goal_distance(achieved_goal, desired_goal)
        food_reward = 2
        # if self.load_food:
        #     food_spoon_distance = self._compute_goal_distance(
        #         info['food_position'],
        #         info['spoon_position']
        #     )
        #     food_reward = -(food_spoon_distance > self.food_tolerance).astype(np.float32) + 2

        if self.reward_type == 'sparse':
            return -(distance > self.tolerance).astype(np.float32) + food_reward
        else:
            return -distance + food_reward

    def heuristic(self):
        position = self._get_target_position()
        joint_positions = self.ik_controller.calculate_ik_recursive(
            position,
            eef_orn=self.eef_orn
        )
        self._set_kinova_joints_directly(joint_positions)

    def teaching(self, num_steps=50, render=False):
        init_pos = self._get_eef_position()
        final_pos = self._get_target_position()
        trajs = sine_interpolate(init_pos, final_pos, num_steps)
        for i in range(num_steps):
            joint_positions = self.ik_controller.calculate_ik_recursive(
                unity_eef_pos=trajs[i],
                eef_orn=self.eef_orn
            )
            self._set_kinova_joints(joint_positions)
            if render:
                save_image(
                    self.render(),
                    '/home/haoyuan/workspace/rfuniverse/RCareSim/Feeding/feeding_traj_{}.png'.format(i)
                )

    def _get_obs(self):
        kinova_obs = self._get_eef_position()
        spoon_obs = self._get_spoon_position()
        if self.load_food:
            food_obs = self._get_food_position()
        else:
            food_obs = []
        human_obs = self.neck_head_rot.copy()
        target_obs = self._get_target_position()

        obs = np.concatenate((kinova_obs, spoon_obs, food_obs, human_obs, target_obs))
        if self.load_food:
            achieved_goal = food_obs.copy()
        else:
            achieved_goal = spoon_obs.copy()

        return {
            'observation': obs.copy(),
            'achieved_goal': achieved_goal.copy(),
            'desired_goal': self.goal.copy()
        }

    def _compute_goal_distance(self, goal_a, goal_b):
        assert goal_a.shape == goal_b.shape
        return np.linalg.norm(goal_a - goal_b, axis=-1)

    def _load_food(self):
        self.rigidbody_channel.set_action(
            'LoadRigidbody',
            filename=self.asset_bundle_file,
            name='FoodSphere',
            position=self._get_spoon_position()
        )
        self._step()

    def _destroy_food(self):
        self.rigidbody_channel.set_action(
            'Destroy',
            index=0
        )
        self._step()

    def _randomize_neck_head(self):
        return self.np_random.uniform(
            self.neck_head_rotation_min,
            self.neck_head_rotation_max
        )

    def _set_human_neck_head(self):
        neck_rot = [float(self.neck_head_rot[0]), 0, 0]
        head_rot = [0, float(self.neck_head_rot[1]), 0]
        self.game_object_channel.set_action(
            'SetTransform',
            index=2,
            rotation=neck_rot
        )
        self._step()
        self.game_object_channel.set_action(
            'SetTransform',
            index=3,
            rotation=head_rot
        )
        self._step()

    def _get_target_position(self):
        return np.array(self.game_object_channel.data[1]['position'])

    def _get_spoon_position(self):
        return np.array(self.game_object_channel.data[0]['position'])

    def _get_food_position(self):
        return np.array(self.rigidbody_channel.data[0]['position'])

    def _get_eef_position(self):
        return np.array(self.articulation_channel.data[1]['positions'][11])

    def _set_kinova_joints(self, joint_positions):
        self.articulation_channel.set_action(
            'SetJointPosition',
            index=0,
            joint_positions=list(joint_positions[0:7]),
        )
        self._step()

    def _set_kinova_joints_directly(self, joint_positions):
        # Reset Kinova
        self.articulation_channel.set_action(
            'SetJointPositionDirectly',
            index=0,
            joint_positions=list(joint_positions[0:7]),
        )
        self._step()

        # Reset Robotiq85
        self.articulation_channel.set_action(
            'SetJointPositionDirectly',
            index=1,
            joint_positions=[40, 40]
        )
        self._step()

    def _check_success(self, obs):
        achieved_goal = obs['achieved_goal']
        desired_goal = obs['desired_goal']
        distance = self._compute_goal_distance(achieved_goal, desired_goal)

        return (distance < self.tolerance).astype(np.float32)

    def _check_food_fall(self, info):
        food_spoon_distance = self._compute_goal_distance(
            info['food_position'],
            info['spoon_position']
        )

        return float(food_spoon_distance) > self.food_tolerance
