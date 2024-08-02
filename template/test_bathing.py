import os
import time
import numpy as np
from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

def main():
    # Set the path to the Unity executable file
    UNITY_EXECUTABLE_PATH = "<YourPathHere>"

    # Initialize the environment
    env = RCareWorld(executable_file=UNITY_EXECUTABLE_PATH)
    env.DebugObjectPose()
    env.SetTimeStep(0.005)
    env.step()

    # Instantiate BathingScoreAttr and SpongeAttr
    bathing_score = env.InstanceObject(name="BathingScore", id=1, attr_type=attr.BathingScoreAttr)
    sponge = env.InstanceObject(name="Sponge", id=2, attr_type=attr.SpongeAttr)
    
    # Create the robot
    robot = env.InstanceObject(name="franka_panda", id=123456, attr_type=attr.ControllerAttr)
    robot.SetIKTargetOffset(position=[0, 0.105, 0])
    env.step()

    # Grasp the sponge
    sponge_position = sponge.data['position']
    robot.IKTargetDoMove(position=sponge_position, duration=0, speed_based=False)
    robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
    robot.WaitDo()
    env.step()
    robot.grasp(sponge.id)
    env.step()

    # Move the sponge to the water tank
    water_tank_position = [0.5, 0.2, 0.5]  # Adjust as necessary
    robot.IKTargetDoMove(position=water_tank_position, duration=2, speed_based=False)
    robot.WaitDo()
    env.step()
    sponge.SetTransform(position=water_tank_position)
    env.step()

    # Simulate dipping the sponge in the water
    for _ in range(20):
        new_position = [water_tank_position[0], water_tank_position[1] - 0.1, water_tank_position[2]]
        sponge.SetTransform(position=new_position)
        env.step()

    # Move the sponge to the manikin
    manikin_position = [0.3, 0.5, 0.3]  # Adjust as necessary
    robot.IKTargetDoMove(position=manikin_position, duration=2, speed_based=False)
    robot.WaitDo()
    env.step()
    sponge.SetTransform(position=manikin_position)
    env.step()

    # Simulate the bathing process and calculate scores
    start_time = time.time()
    while time.time() - start_time < 10:  # Adjust duration as necessary
        forces = sponge.data['forces']
        prop = sponge.data['proportion']

        if forces:
            all_nonzero_forces = [force for force in forces if force > 0]
            forces_score = attr.sponge_attr.score_forces(all_nonzero_forces)
            print(f"Forces Score: {forces_score}")

        if prop is not None:
            print(f"Bathing Score: {prop}")

        # Display real-time scores
        scores = bathing_score.get_scores()
        print(f"Current Scores: {scores}")

        env.step()

    # Save final scores to file
    score_file_path = "./bathing_scores.json"
    bathing_score.save_scores_to_file(score_file_path)
    print(f"Final scores saved to {score_file_path}")

    # Close the environment
    env.close()

if __name__ == "__main__":
    main()
