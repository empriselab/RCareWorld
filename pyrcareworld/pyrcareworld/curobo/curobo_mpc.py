from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.types.state import JointState as CuJointState
from curobo.wrap.reacher.mpc import MpcSolver, MpcSolverConfig
from curobo.geom.sdf.world import CollisionCheckerType
from curobo.geom.types import WorldConfig
from curobo.util_file import get_robot_configs_path, get_world_configs_path, join_path, load_yaml
from curobo.rollout.rollout_base import Goal

import numpy as np
import time
import random
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import os
import torch


class KinovaCuroboMPCMove:
    def __init__(self):
        # Init RCareWorld and robot
        self.env = RCareWorld()
        self.env.step(10)
        self.robot = self.env.GetAttr(315893)
        self.env.step(10)
        self.robot.SetPosition([0, 0, 0])
        self.env.step(10)

        print("Setting initial robot pose...")
        self.robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0, speed_based=False)
        self.robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        self.robot.WaitDo()
        self.env.step(10)
        print("Initialization complete!")

        # Init Curobo MPC
        self.tensor_args = TensorDeviceType()

        robot_cfg = load_yaml(join_path(get_robot_configs_path(), "kinova_gen3.yml"))["robot_cfg"]
        world_cfg_table = WorldConfig.from_dict(load_yaml(join_path(get_world_configs_path(), "collision_table.yml")))
        world_cfg_mesh = WorldConfig.from_dict(load_yaml(join_path(get_world_configs_path(), "collision_table.yml"))).get_mesh_world()
        world_cfg_mesh.mesh[0].pose[2] = -10.0

        self.world_cfg = WorldConfig(cuboid=world_cfg_table.cuboid, mesh=world_cfg_mesh.mesh)

        self.mpc_config = MpcSolverConfig.load_from_robot_config(
            robot_cfg,
            self.world_cfg,
            use_cuda_graph=True,
            use_cuda_graph_metrics=True,
            use_cuda_graph_full_step=False,
            self_collision_check=True,
            collision_checker_type=CollisionCheckerType.MESH,
            # collision_cache={"obb": n_obstacle_cuboids, "mesh": n_obstacle_mesh},
            use_mppi=True,
            use_lbfgs=False,
            use_es=False,
            store_rollouts=True,
            step_dt=0.02,
        )
        self.mpc = MpcSolver(self.mpc_config)
        self.joint_names = self.mpc.rollout_fn.joint_names
        self.current_state = CuJointState.from_position(torch.zeros(1, len(self.joint_names), device=self.tensor_args.device), joint_names=self.joint_names)

        retract_cfg = self.mpc.rollout_fn.dynamics_model.retract_config.clone().unsqueeze(0)
        joint_names = self.mpc.rollout_fn.joint_names

        state = self.mpc.rollout_fn.compute_kinematics(
            JointState.from_position(retract_cfg, joint_names=joint_names)
        )
        current_state = JointState.from_position(retract_cfg, joint_names=joint_names)
        retract_pose = Pose(state.ee_pos_seq, quaternion=state.ee_quat_seq)
        goal = Goal(
            current_state=current_state,
            goal_state=JointState.from_position(retract_cfg, joint_names=joint_names),
            goal_pose=retract_pose,
        )

        goal_buffer = self.mpc.setup_solve_single(goal, 1)
        self.mpc.update_goal(goal_buffer)
        mpc_result = self.mpc.step(current_state, max_attempts=2)
        # print(mpc_result)

        self.target = self.env.GetAttr(2345)

        print("Curobo MPC initialized.")

    def get_joint_state(self):
        joint_pos_deg = self.robot.data['joint_positions']
        joint_pos_rad = [np.deg2rad(x) for x in joint_pos_deg]
        return CuJointState.from_position(torch.tensor(joint_pos_rad, device=self.tensor_args.device).unsqueeze(0), joint_names=self.joint_names)

    def move_to_pose(self, position, orientation=[0.0, 0.0, 0.0, 1.0]):
        pose = Pose(
            position=torch.as_tensor(position, device=self.tensor_args.device).unsqueeze(0),
            quaternion=torch.as_tensor(orientation, device=self.tensor_args.device).unsqueeze(0),
        )

        self.current_state = self.get_joint_state()
        goal = Goal(
            current_state=self.current_state,
            goal_state=JointState.from_position(pose, joint_names=self.joint_names),
            goal_pose=pose,
        )

        goal_buffer = self.mpc.setup_solve_single(goal, 1)
        self.mpc.update_goal(goal_buffer)

        result = self.mpc.step(self.current_state, max_attempts=2)

        if result.success:
            return self.execute_trajectory(result.js_action)
        else:
            print("MPC failed to find solution.")
            return False

    def execute_trajectory(self, joint_trajectory: CuJointState):
        joint_positions = joint_trajectory.position.squeeze().cpu().numpy()
        for i in range(0, len(joint_positions), 4):
            joint_slice = joint_positions[i]
            joint_tensor = torch.tensor([joint_slice], device=self.tensor_args.device, dtype=self.tensor_args.dtype)
            ee_state = self.mpc.rollout_fn.compute_kinematics(CuJointState.from_position(joint_tensor, joint_names=self.joint_names))
            ee_pos = ee_state.ee_pos_seq.cpu().numpy()[0]

            self.robot.IKTargetDoMove(position=ee_pos.tolist(), duration=0.5, speed_based=False)
            self.robot.WaitDo()
            self.env.step(5)
        return True

    def create_cube(self, cube_id, position):
        """Create a cube at specified position"""
        try:
            original_cube = self.env.GetAttr(1)
            cube = original_cube.Copy(cube_id)
            cube.SetTransform(
                position=position,
                scale=[0.02, 0.02, 0.02],
            )
            self.env.step(50)
            return cube
        except Exception as e:
            print(f"Failed to create cube: {e}")
            return None

    def get_random_position(self, base_position, radius=0.1):
        """Generate a random position near the base position"""
        x = base_position[0] + random.uniform(-radius, radius)
        y = base_position[1]
        z = base_position[2] + random.uniform(-radius, radius)
        return [x, y, z]

    def close(self):
        self.env.close()

    
    def run(self, num_cycles=10):
        # Initial positions for cubes
        cube1_pos = [-0.4, 0.03, 0.4]
        cube2_pos = [0.4, 0.03, 0.4]
        
        # Create initial cubes
        cube1 = self.create_cube(111111, cube1_pos)
        cube2 = self.create_cube(222222, cube2_pos)
        
        if cube1 is None or cube2 is None:
            print("Failed to create initial cubes")
            return
        
        try:
            for i in range(num_cycles):
                print(f"\nStarting cycle {i+1}...")
                
                # Move to cube1
                print("Moving to cube1...")
                if not self.move_to_pose(cube1_pos):
                    print("Failed to move to cube1")
                    break
                
                # Move to cube2
                print("Moving to cube2...")
                if not self.move_to_pose(cube2_pos):
                    print("Failed to move to cube2")
                    break
                
                # Delete and recreate cube1
                print("Regenerating cube1...")
                cube1.Destroy()
                self.env.step(10)
                cube1_pos = self.get_random_position(cube1_pos)
                cube1 = self.create_cube(111111, cube1_pos)

                time.sleep(1)
        
        finally:
            print("Cleaning up...")
            if cube1:
                cube1.Destroy()
            if cube2:
                cube2.Destroy()
                
                

if __name__ == "__main__":
    print("Starting KinovaCuroboMPCMove...")
    controller = KinovaCuroboMPCMove()
    # controller.run(num_cycles=10)
    # print("Program execution completed!")
