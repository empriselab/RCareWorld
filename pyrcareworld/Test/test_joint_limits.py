import random
from pyrcareworld.envs.rcareworld_env import RCareWorld

# Script to test joint limits. Paired with `Set Joint Limits` scene.
if __name__ == "__main__":
    env = RCareWorld()

    # Corresponds to the human in the scene.
    person = env.create_human(id=100, name="Person", is_in_scene=True)

    for _ in range(10000):
        # Randomly selects a set of 3 upper and lower joint limits every frame.
        lower1, upper1 = random.uniform(-50, 0), random.uniform(1, 50)
        lower2, upper2 = random.uniform(-50, 0), random.uniform(1, 50)
        lower3, upper3 = random.uniform(-50, 0), random.uniform(1, 50)

        # Sets the joint limits of LeftUpperArm, LeftHand, and RightHand.
        person.setJointLimits("LeftUpperArm", lower1, upper1)
        person.setJointLimits("LeftHand", lower2, upper2, "X")
        person.setJointLimits("RightHand", lower3, upper3, "Z")

        # You should observe the joint limits being set in the Unity scene.
        # (Causes the human mesh to spasm due to the random joint limits.)

        print(
            "Setting joint limits to:\n\tLeftUpperArm: ",
            lower1,
            upper1,
            "\n\tLeftHand: ",
            lower2,
            upper2,
            "\n\tRightHand: ",
            lower3,
            upper3,
            "\n\n",
        )

        env.step()
