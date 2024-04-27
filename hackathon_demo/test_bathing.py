from pyrcareworld.envs import RCareWorld
from pyrcareworld.attributes import sponge_attr
import random

# Script to test bed bathing in hackathon.
if __name__ == "__main__":
    # connect with the Unity environment
    # Change the path to the Unity executable file
    env = RCareWorld(
        executable_file="<YOurPathHere>"
    )

    # A collection of all force readings over all steps.
    all_nonzero_forces = []

    # Create a robot and a target object
    # Control the robot arm
    robot = env.create_robot(
        id=123456, gripper_list=[123456], robot_name="stretch3", base_pos=[0, 0, 0]
    )
    # Control the robot base
    robot_base = env.create_robot(id = 12346, robot_name = 'mobile_base', base_pos = [0, 0, 1])
    # The red cuba in the environment
    target = env.create_object(id=2333, name="Cube", is_in_scene=True)
    # Move the robot to the target object
    for i in range(10):
        position = target.getPosition()
        # print(position)
        robot.BioIKMove(position)
        env.step()
    # Move the robot base, don't move faster than this
    for i in range(100):
        position = robot_base.getRobotState()["position"]
        position[2]+=0.004
        print(position)
        robot_base.setTransform(position)
        env.step()
    while True:
        position = target.getPosition()
        rotation = target.getRotation()
        robot.directlyMoveTo(position)

        # force on the sponge
        forces = env.instance_channel.data[509]["forces"]
        # painted area
        prop = env.instance_channel.data[509]["proportion"]
        msg = ""
        if len(forces) > 0:
            for force in forces:
                all_nonzero_forces.append(force)

            msg += (
                "Forces Score: "
                + str(sponge_attr.score_forces(all_nonzero_forces))
                + "\n"
            )

        if prop != None:
            msg += "Bathing Score: " + str(prop) + "\n"
        if len(msg) > 0:
            msg += "*************"
            print(msg)

        env.step()