import pybullet as p
import pybullet_data
import numpy as np
import math


class RFUniverseStretchController:
    """
    RFUniverseController is a class to generate robot arm joint states. In simulation environment, we mostly
    want to specify the 6DoF of a joint, then the robot arm will automatically move to that state. Thus, here
    we use pybullet.calculateInverseKinematics() to generate joint positions based on a given robot arm, a
    given end-effector joint and a target Cartesian position. The generated joint states will be passed to
    Unity by rfuniverse channels. Besides, this class will also provide functions to align coordinate in Unity
    and in pybullet.
    """

    def __init__(
        self,
        robot_urdf,
        base_pos=np.array([0, 0, 0]),
        base_orn=[-0.707107, 0.0, 0.0, 0.707107],
        init_joint_positions=[0] * 12,
        render=False,
    ):
        if render:
            p.connect(p.GUI)  # For debug mode
        else:
            p.connect(p.DIRECT)

        p.configureDebugVisualizer(p.COV_ENABLE_Y_AXIS_UP, 1)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, -9.8, 0)

        self.bullet_client = p
        self.bullet_flags = self.bullet_client.URDF_ENABLE_CACHED_GRAPHICS_SHAPES

        self.robot_name = "stretch"
        self.robot_urdf = robot_urdf
        self.end_effector_id = 15
        self.num_dof = 12
        self.init_joint_positions = self.get_pybullet_joint_pos_from_unity(
            init_joint_positions
        )
        self.robot = self.bullet_client.loadURDF(
            self.robot_urdf,
            base_pos,
            base_orn,
            useFixedBase=True,
            flags=self.bullet_flags,
        )

        self.moveable_joint_ids = []
        joint_position_idx = 0
        self.revolute_idx = []
        self.prismatic_idx = []
        for j in range(36):
            self.bullet_client.changeDynamics(
                self.robot, j, linearDamping=0, angularDamping=0
            )
            info = self.bullet_client.getJointInfo(self.robot, j)

            jointName = info[1]
            jointType = info[2]
            if (
                jointType == self.bullet_client.JOINT_REVOLUTE
                or jointType == self.bullet_client.JOINT_PRISMATIC
            ):
                # print(j, jointName)
                self.moveable_joint_ids.append(j)
                if jointType == self.bullet_client.JOINT_REVOLUTE:
                    self.revolute_idx.append(joint_position_idx)
                elif jointType == self.bullet_client.JOINT_PRISMATIC:
                    self.prismatic_idx.append(joint_position_idx)
                joint_position_idx += 1

        self.reset()

        # print('pybullet', self.get_link_state(self.end_effector_id))

    def get_bullet_pos_from_unity(self, unity_pos: list) -> list:
        return [-1 * unity_pos[0], unity_pos[1], unity_pos[2]]

    def get_unity_pos_from_bullet(self, bullet_pos: list) -> list:
        return [-1 * bullet_pos[0], bullet_pos[1], bullet_pos[2]]

    def get_unity_joint_pos_from_pybullet(self, pybullet_joint_pos: tuple) -> list:
        pybullet_joint_pos = list(pybullet_joint_pos)[: self.num_dof]
        for i, (joint_pos) in enumerate(pybullet_joint_pos):
            if i in self.revolute_idx:
                pybullet_joint_pos[i] = 180 * joint_pos / math.pi

        # The order of joints in Unity and Pybullet is not same.
        # So we need to change the order manually here as well as ignoring the rotation of wheel.
        unity_joint_pos = (
            list(pybullet_joint_pos[10:12])
            + list(pybullet_joint_pos[2:8])
            + [pybullet_joint_pos[9], pybullet_joint_pos[8]]
        )

        return unity_joint_pos

    def get_pybullet_joint_pos_from_unity(self, unity_joint_pos: list) -> list:
        unity_joint_pos = list(unity_joint_pos)[: self.num_dof]
        unity_joint_pos = np.array(unity_joint_pos)
        pybullet_joint_pos = unity_joint_pos * math.pi / 180

        return pybullet_joint_pos

    def calculate_ik(self, unity_eef_pos, eef_orn=None) -> list:
        if eef_orn is None:
            eef_orn = self.bullet_client.getQuaternionFromEuler(
                [math.pi / 2.0, 0.0, 0.0]
            )

        eef_pos = self.get_bullet_pos_from_unity(unity_eef_pos)

        joint_positions = self.bullet_client.calculateInverseKinematics(
            self.robot, self.end_effector_id, eef_pos, eef_orn, maxNumIterations=20
        )

        for i, (idx) in enumerate(self.moveable_joint_ids):
            self.bullet_client.resetJointState(self.robot, idx, joint_positions[i])

        return self.get_unity_joint_pos_from_pybullet(joint_positions)

    def calculate_ik_recursive(self, unity_eef_pos, eef_orn=None) -> list:
        if eef_orn is None:
            eef_orn = self.bullet_client.getQuaternionFromEuler(
                [math.pi / 2.0, 0.0, 0.0]
            )

        eef_pos = self.get_bullet_pos_from_unity(unity_eef_pos)
        for i in range(20):
            joint_positions = self.bullet_client.calculateInverseKinematics(
                self.robot, self.end_effector_id, eef_pos, eef_orn, maxNumIterations=20
            )

            for i, (idx) in enumerate(self.moveable_joint_ids):
                self.bullet_client.resetJointState(self.robot, idx, joint_positions[i])

        return self.get_unity_joint_pos_from_pybullet(joint_positions)

    def get_link_state(self, link_idx):
        link_state = self.bullet_client.getLinkState(self.robot, link_idx)

        return self.get_unity_pos_from_bullet(link_state[0])

    def reset(self):
        for i, (idx) in enumerate(self.moveable_joint_ids):
            self.bullet_client.resetJointState(
                self.robot, idx, self.init_joint_positions[i]
            )
