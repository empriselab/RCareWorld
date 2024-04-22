from pyrcareworld.envs import RCareWorld
from pyrcareworld.attributes import sponge_attr
import random

# Script to test bed bathing in hackathon.
if __name__ == "__main__":
    env = RCareWorld(
        executable_file="/home/cathy/Workspace/RCareUnity/Build/Bathing/Ubuntu/bathing_ubuntu.x86_64"
    )

    # A collection of all force readings over all steps.
    all_nonzero_forces = []

    # robot = env.create_robot(
    #     id=12345, gripper_list=["123450"], robot_name="stretch3", base_pos=[0, 0, 0]
    # )
    target = env.create_object(id=2333, name="Cube", is_in_scene=True)
    for i in range(10):
        env.step()
    while True:
        position = target.getPosition()
        rotation = target.getRotation()
        # robot.directlyMoveTo(position)

        # All new forces, assumed to be non-zero by Unity.
        forces = env.instance_channel.data[509]["forces"]
        # New proportion, or None if not updated.
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
