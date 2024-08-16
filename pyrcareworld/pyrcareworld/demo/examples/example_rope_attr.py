from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
import pyrcareworld.utils.rfuniverse_utility as utility
import numpy as np
import math
from typing import Optional
import matplotlib.pyplot as plt


class KinovaRope(RCareWorld):
    def __init__(
        self,
        executable_file: str = None,
        scene_file: str = None,
        assets: list = [],
        graphics: bool = True,
        port: int = 5004,
        proc_id=0,
        log_level=0,
        ext_attr: list[attr.BaseAttr] = [],
        check_version: bool = True
    ):
        RCareWorld.__init__(
            self,
            executable_file=executable_file,
            scene_file=scene_file,
            assets=assets,
            graphics=graphics,
            port=port,
            proc_id=proc_id,
            log_level=log_level,
            ext_attr=ext_attr,
            check_version=check_version
        )

        robot = self.GetAttr(221584)
        gripper = self.GetAttr(2215840)
        cube = self.GetAttr(45678)
        rope = self.GetAttr(45902)
        
        self.rope = rope
        
        self.robot_dof = 7
        
        self.robot = robot
        self.cube = cube
        print("Initialized RCareStorm Kinova object!")

        self.cube_pos = self.cube.data["position"]
        self.cube_rot = self.cube.data["rotation"]
        print("position", self.cube_pos)
        robot.IKTargetDoMove(position=self.cube_pos, duration=0.1, relative=False)
        robot.IKTargetDoComplete()

        self.step()
        while not self.robot.data["move_done"]:
            self.step()
        print("Moved robot to reference cube!")
        
        robot.IKTargetDoRotateQuaternion(
            quaternion=utility.UnityEulerToQuaternion([180, 0, 0]),
            duration=0.1,
            relative=True,
        )
        robot.IKTargetDoComplete()
        gripper.GripperClose()
        self.step()
        while not robot.data["move_done"]:
            self.step()
        
        
        self.rope.GetParticles()
        self.robot.EnabledNativeIK(False)
        self.step()
        
        
        # self.Pend()
        #     self.instance_channel.set_action(
        #         "IKTargetDoRotate",
        #         id=self.robot_id,
        #         vector3=[0, 0, 0],
        #         duration=0,
        #         speed_based=False,
        # )
        # self._step()
        # print("Rotated robot to reference cube!")

    def get_robot_joint_positions(self):
        return self.robot.data['joint_positions']

    def get_robot_joint_velocities(self):
        return self.robot.data['joint_velocities']

    def get_robot_joint_accelerations(self):
        return self.robot.data['joint_accelerations']

    def get_target_eef_pose(self):
        target_pose = {}
        target_pose['position'] = self.cube.data['position']
        target_pose['orientation'] = self.cube.data['rotation']
        return target_pose
        
    def set_robot_joint_position(self, joint_positions=None, joint_velocities=None):
        
        if joint_positions is not None:
            self.robot.SetJointPositionDirectly(joint_positions)
            self.step()
        
        if joint_velocities is not None:
            self.robot.SetJointVelocity(joint_velocities)
            self.step()

    def get_particle_positions(self):
        if "particles" in self.rope.data:
            return self.rope.data["particles"]
        else:
            self.rope.GetParticles()
            self.step()
            return self.rope.data["particles"]
    

    def step(self):
        self._step()
        
if __name__ == "__main__":
    env = RCareWorld()
    # print(test_env.get_robot_joint_positions())
    rope = env.GetAttr(356793)
    env.step(100)
    
    rope.GetParticles()
    
    env.step(100)

    print("ROPE", rope.data["particles"])
    env.step(10)
    
    rope.GetParticleGroup()
    env.step(100)
    
    print("PARTICLE GROUP", rope.data["particlegroups"])
    env.step(100)



    # while not rope.GetParticles():
    #     env.step()
    #     print("particles",rope.GetParticles())
    #     env.step()

    def visualize_3d_points(points, i):
        """
        Visualize a list of 3D points and save the plot to a file.

        Parameters:
        points (list of tuple or list): A list of points in 3D space (x, y, z).
        i (int): An integer to help name the output file.
        """
        # Extract x, y, z coordinates from the points
        x = [point[0] for point in points]
        y = [point[1] for point in points]
        z = [point[2] for point in points]

        # Create a new figure for the 3D plot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Scatter plot
        ax.scatter(x, y, z, c='b', marker='o')

        # Set labels
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        # Save the plot to a file
        filename = f'3d_points_plot_{i}.png'
        plt.savefig(filename)
        plt.close()

        print(f'Plot saved as {filename}')

    
    
    for i in range(3):
        env.step()
        print(rope.GetParticles())
        if "particles" in rope.data:
            print("rope",rope.data["particles"])
            visualize_3d_points(rope.data["particles"], i)
        
            
            
            
        if "particlegroups" in rope.data:
            print("particlegroups", rope.data["particlegroups"])
        else:
            print("no particlegroups")
            
            
        print("====================================")
        print(rope.data)
        print("====================================")       
        
    while True:
        env.step()
   

    
    
    

    
    
    