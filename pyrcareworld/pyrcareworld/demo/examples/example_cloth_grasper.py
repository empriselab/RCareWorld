# import os
# import sys
# import random

# # Add the project directory to the system path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# from pyrcareworld.envs.base_env import RCareWorld
# import pyrcareworld.attributes as attr
# from pyrcareworld.demo import mesh_path

# from pyrcareworld.demo import executable_path
# # Initialize the environment with the specified scene file
# player_path = os.path.join(executable_path, "Player/Player.x86_64")

# # Initialize the environment
# env = RCareWorld(assets=["kinova_gen3_robotiq85"], executable_file=player_path)
# env.SetTimeStep(0.005)
# env.DebugObjectPose()
# env.EnabledGroundObiCollider(True)

# # Load the T-shirt mesh
# t_shirt_path = os.path.join(mesh_path, 'Tshirt.obj')
# mesh = env.LoadCloth(path=t_shirt_path)
# mesh.SetTransform(position=[0, 1, 0])

# # Perform initial simulation steps to stabilize the cloth
# env.step(200)

# # Get particles data from the mesh
# mesh.GetParticles()
# env.step()
# print(mesh.data)

# # Extract positions of specific particles
# position1 = mesh.data['particles'][500]
# position2 = mesh.data['particles'][200]

# # Create point objects at the positions of the selected particles
# point1 = env.InstanceObject("Empty")
# point1.SetTransform(position=position1)
# mesh.AddAttach(point1.id)

# point2 = env.InstanceObject("Empty")
# point2.SetTransform(position=position2)
# mesh.AddAttach(point2.id)

# env.step()

# # Move the points to the initial positions
# point1.DoMove([-0.25, 1, 0], 2, speed_based=False)
# point2.DoMove([0.25, 1, 0], 2, speed_based=False)
# point2.WaitDo()

# # Initialize the Kinova robot
# robot = env.InstanceObject(name="kinova_gen3_robotiq85", id=123456, attr_type=attr.ControllerAttr)
# robot.SetPosition([0, 0, 0])
# env.step()

# # Get the gripper attribute and open the gripper
# gripper = env.GetAttr(1234560)
# gripper.GripperOpen()

# # Move the robot to the first point, grab it, and move it to a new position
# robot.IKTargetDoMove(position=[-0.25, 1, 0], duration=2, speed_based=False)
# robot.WaitDo()
# robot.IKTargetDoMove(position=[-0.25, 1, 0.5], duration=2, speed_based=False)
# robot.WaitDo()
# gripper.GripperClose()
# env.step(50)

# robot.IKTargetDoMove(position=[0, 1.5, 0], duration=2, speed_based=False)
# robot.WaitDo()

# robot.IKTargetDoMove(position=[0.25, 1.5, 0], duration=2, speed_based=False)
# robot.WaitDo()
# gripper.GripperOpen()
# env.step(50)

# # Main loop to oscillate the points
# while True:
#     # Move the points backward
#     point1.DoMove([-0.25, 1, -0.5], 1)
#     point2.DoMove([0.25, 1, -0.5], 1)
#     point2.WaitDo()

#     # Move the points forward
#     point1.DoMove([-0.25, 1, 0.5], 1)
#     point2.DoMove([0.25, 1, 0.5], 1)
#     point2.WaitDo()

# # Close the environment
# env.Pend()
# env.close()
