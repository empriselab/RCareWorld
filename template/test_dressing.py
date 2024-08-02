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

    # Instantiate DressingScoreAttr and ClothAttr
    dressing_score = env.InstanceObject(name="DressingScore", id=1, attr_type=attr.DressingScoreAttr)
    cloth = env.InstanceObject(name="Cloth", id=2, attr_type=attr.ClothAttr)
    
    # Create the robot
    robot = env.InstanceObject(name="franka_panda", id=123456, attr_type=attr.ControllerAttr)
    robot.SetIKTargetOffset(position=[0, 0.105, 0])
    env.step()

    # Move the robot to the cloth
    cloth_position = cloth.data['position']
    robot.IKTargetDoMove(position=cloth_position, duration=0, speed_based=False)
    robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
    robot.WaitDo()
    env.step()
    robot.grasp(cloth.id)
    env.step()

    # Move the robot to the manikin
    manikin_position = [0.3, 0.5, 0.3]  # Adjust as necessary
    robot.IKTargetDoMove(position=manikin_position, duration=2, speed_based=False)
    robot.WaitDo()
    env.step()

    # Simulate moving the cloth to the manikin
    start_time = time.time()
    while time.time() - start_time < 10:  # Adjust duration as necessary
        # Horizontal movement
        new_position = [manikin_position[0] + 0.1 * np.sin(time.time()), manikin_position[1], manikin_position[2]]
        robot.IKTargetDoMove(position=new_position, duration=0.1, speed_based=False)
        robot.WaitDo()
        env.step()

        # Check for contact with the manikin
        cloth_particles = cloth.data.get('particles', [])
        manikin_collider = manikin_position  # Simplified for this example

        for particle in cloth_particles:
            if np.linalg.norm(np.array(particle) - np.array(manikin_collider)) < 0.05:  # Adjust threshold as necessary
                print("Contact detected, releasing cloth.")
                robot.release(cloth.id)
                env.step()
                break

        # Display real-time scores
        scores = dressing_score.get_scores()
        print(f"Current Scores: {scores}")

        env.step()

    # Save final scores to file
    score_file_path = "./dressing_scores.json"
    dressing_score.save_scores_to_file(score_file_path)
    print(f"Final scores saved to {score_file_path}")

    # Close the environment
    env.close()

if __name__ == "__main__":
    main()
