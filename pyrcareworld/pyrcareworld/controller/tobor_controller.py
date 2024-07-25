import pybullet as p
import pybullet_data
import numpy as np
import math
import os


class RFUniverseToborController:
    def __init__(
        self,
        urdf_folder,
        left_base_pos=np.array([0.07, 1, 0.22]),
        left_base_orn=p.getQuaternionFromEuler([-math.pi / 2, math.pi, -math.pi / 2]),
        left_hand="robotiq85",
        right_base_pos=np.array([-0.07, 1, 0.22]),
        right_base_orn=p.getQuaternionFromEuler([-math.pi / 2, 0, math.pi / 2]),
        right_hand="dhag95",
        ik_tolerance=0.03,
        render=False,
        left_init_joint_positions=[0] * 7,
        right_init_joint_positions=[0] * 7,
        revise=False,
    ):
        self.revise = revise
        if render:
            p.connect(p.GUI)
        else:
            p.connect(p.DIRECT)
        p.configureDebugVisualizer(p.COV_ENABLE_Y_AXIS_UP, 1)
        p.setAdditionalSearchPath(urdf_folder)
        p.setGravity(0, -9.8, 0)
        self.bullet_client = p
        self.bullet_flags = self.bullet_client.URDF_ENABLE_CACHED_GRAPHICS_SHAPES

        self.urdf_folder = urdf_folder
        self.left_base_pos = left_base_pos
        self.left_base_orn = left_base_orn
        self.left_hand_name = left_hand
        self.left_urdf = "tobor_arm_" + self.left_hand_name + ".urdf"

        self.right_base_pos = right_base_pos
        self.right_base_orn = right_base_orn
        self.right_hand_name = right_hand
        self.right_urdf = "tobor_arm_" + self.right_hand_name + ".urdf"

        self._load_urdf()
        self.ik_tolerance = ik_tolerance

        # end_effector_id: 7 robot arm joints plus 1 fixed joint for grasp point
        self.end_effector_id = 7
        self.num_dof = 7
        self.revolute_joint_ids = list(range(7))
        self.link_ids = list(range(8))

        # revise_factor: fix the positive or negative joint position between pybullet and Unity.
        self.revise_factor_old = np.array([-1, 1, -1, 1, -1, 1, -1])
        self.revise_factor = np.array([1, 1, 1, 1, 1, 1, 1])
        self.init_joint_positions = {
            "left": self.get_pybullet_joint_pos_from_unity(left_init_joint_positions),
            "right": self.get_pybullet_joint_pos_from_unity(right_init_joint_positions),
        }

        self.reset()

        # For debug
        joint_info = self.bullet_client.getJointInfo(self.left_arm_id, 0)
        print(joint_info[1], joint_info[12], joint_info[16])

    def get_bullet_pos_from_unity(self, unity_pos: list) -> list:
        return [-1 * unity_pos[0], unity_pos[1], unity_pos[2]]

    def get_unity_pos_from_bullet(self, bullet_pos: list) -> list:
        return [-1 * bullet_pos[0], bullet_pos[1], bullet_pos[2]]

    def get_unity_joint_pos_from_pybullet(self, pybullet_joint_pos: tuple) -> list:
        pybullet_joint_pos = list(pybullet_joint_pos)[: self.num_dof]
        pybullet_joint_pos = np.array(pybullet_joint_pos)
        if self.revise is True:
            unity_joint_pos = (
                self.revise_factor_old * pybullet_joint_pos * 180 / math.pi
            )
        else:
            unity_joint_pos = self.revise_factor * pybullet_joint_pos * 180 / math.pi

        return unity_joint_pos

    def get_pybullet_joint_pos_from_unity(self, unity_joint_pos: list) -> list:
        unity_joint_pos = list(unity_joint_pos)[: self.num_dof]
        unity_joint_pos = np.array(unity_joint_pos)
        if self.revise is True:
            pybullet_joint_pos = (
                self.revise_factor_old * unity_joint_pos * math.pi / 180
            )
        else:
            pybullet_joint_pos = self.revise_factor * unity_joint_pos * math.pi / 180

        return pybullet_joint_pos

    def calculate_ik(self, mode, unity_eef_pos, eef_orn=None) -> list:
        self._check_mode(mode)
        if mode == "left":
            robot_id = self.left_arm_id
        else:
            robot_id = self.right_arm_id

        if eef_orn is None:
            eef_orn = self.bullet_client.getQuaternionFromEuler(
                [math.pi / 2.0, 0.0, 0.0]
            )

        eef_pos = self.get_bullet_pos_from_unity(unity_eef_pos)

        for j in range(10):
            joint_positions = self.bullet_client.calculateInverseKinematics(
                robot_id, self.end_effector_id, eef_pos, eef_orn, maxNumIterations=20
            )

            for i, (idx) in enumerate(self.revolute_joint_ids):
                self.bullet_client.resetJointState(robot_id, idx, joint_positions[i])

            link_state = self.bullet_client.getLinkState(robot_id, self.end_effector_id)
            distance = self._calculate_distance(link_state[4], eef_pos)
            if distance < self.ik_tolerance:
                break

        return self.get_unity_joint_pos_from_pybullet(joint_positions)

    def get_link_position(self, mode, link_id):
        """
        Return (link_world_position, world_link_frame_position)
        link_world_position: The Cartesian position of center of mass.
        world_link_frame_position: The position of URDF link frame.
        """
        self._check_mode(mode)
        if mode == "left":
            link_state = self.bullet_client.getLinkState(self.left_arm_id, link_id)
        else:
            link_state = self.bullet_client.getLinkState(self.right_arm_id, link_id)

        return (
            self.get_unity_pos_from_bullet(link_state[0]),
            self.get_unity_pos_from_bullet(link_state[4]),
        )

    def get_all_link_positions(self, mode):
        self._check_mode(mode)
        positions = []

        for link_id in self.link_ids:
            link_world_position, world_link_frame_position = self.get_link_position(
                mode, link_id
            )
            positions.append(world_link_frame_position)

        return positions

    def reset(self):
        for i, (idx) in enumerate(self.revolute_joint_ids):
            self.bullet_client.resetJointState(
                self.left_arm_id, idx, self.init_joint_positions["left"][i]
            )
            self.bullet_client.resetJointState(
                self.right_arm_id, idx, self.init_joint_positions["right"][i]
            )

    def _load_urdf(self):
        self.right_arm_id = self.bullet_client.loadURDF(
            self.right_urdf,
            self.right_base_pos,
            self.right_base_orn,
            useFixedBase=True,
            flags=self.bullet_flags,
        )

        self.left_arm_id = self.bullet_client.loadURDF(
            self.left_urdf,
            self.left_base_pos,
            self.left_base_orn,
            useFixedBase=True,
            flags=self.bullet_flags,
        )

    def _check_mode(self, mode):
        assert mode in [
            "left",
            "right",
        ], "Error: Calculating IK must work in mode 'left' or 'right'."

    def _calculate_distance(self, pos1, pos2):
        pos1 = np.array(pos1)
        pos2 = np.array(pos2)
        distance = np.linalg.norm(pos1 - pos2)

        return distance
