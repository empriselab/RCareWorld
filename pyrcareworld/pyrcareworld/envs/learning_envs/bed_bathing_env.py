from pyrcareworld.envs import RCareWorldGymWrapper
from gym import spaces
from gym.utils import seeding
import numpy as np
import pybullet as p
import math


class BedBathingEnv(RCareWorldGymWrapper):
    def __init__(
        self,
        max_steps=100,
        tolerance=0.05,
        shoulder_rotation_min=45,
        shoulder_rotation_max=75,
        elbow_rotation_min=-10,
        elbow_rotation_max=10,
        use_force=False,
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
        # wait for the human to init
        for i in range(100):
            self._step()

        self.robot = self.create_robot(315893, [3158930], "jaco_7dof")
        self.init_pose_obj = self.create_object(12344, "Ini", True)
        ini_world_pose = self.init_pose_obj.getPosition()
        self.eef_orn = p.getQuaternionFromEuler([math.pi / 2.0, -math.pi / 2.0, 0.0])

        self.robot.moveTo(ini_world_pose, self.eef_orn)

        # self.robot.closeGripper()
        for i in range(4000):
            ini_world_pose = self.init_pose_obj.getPosition()
            self.eef_orn = p.getQuaternionFromEuler(
                [math.pi / 2.0, -math.pi / 2.0, 0.0]
            )

            self.robot.moveTo(ini_world_pose, self.eef_orn)
            self._step()
            force = self.robot.getJointForceByID(6)
            print(force)
            print(self.instance_channel.data[315893])

        # For plotting force
        # self.episodic_forces = []
        # self.episodic_id = 0

    def step(self, action: np.ndarray):
        a = action.copy()
        pos_ctrl = a * 0.3
        curr_pos = self.robot.getGripperPosition()
        pos_ctrl = curr_pos + pos_ctrl
        self.robot.MoveTo(pos_ctrl)
        self._step()
        self.t += 1

        obs = self._get_obs()
        done = False
        reward = self.compute_reward(
            self.robot.getGripperPosition(), self.get_target_position(), None
        )
        success = self._check_success()
        if success or self.t == self.max_steps:
            done = True
        info = {"is_success": float(success)}
        self.episodic_forces.append(np.sum(self._get_force()))
        return obs, reward, done, info

    def reset(self):
        self.env.reset()
        self.t = 0
        self.robot.reset()
        self.robot.setJointPositionsDirectly(self.init_joint_positions)
        self._reset_human()
        # self.teaching_seq_id = 0

        hand_position = self.get_hand_position()

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
    env = BedBathingEnv()
    # while True:
    #     env.get_obs()
    #     env.reset()
    #     env.robot.moveTo(env.hand.getPosition())
    #     for i in range(100):
    #         env._step()
