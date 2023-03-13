from pyrcareworld.envs import RCareWorld

env = RCareWorld()
env.create_robot(id = 639787, gripper_list = ['6397870'], robot_name= 'franka_panda', base_pos=[0, 0, 1])
franka = env.get_robot(639787)
franka.BioIKMove(targetPose=[0,0,-0.5], duration=0.1, relative=True)
franka.BioIKRotateQua(taregetEuler=[90, 0, 0], duration=30, relative=True)

env.close()