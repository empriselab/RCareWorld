from pyrcareworld.envs.base_env import RCareWorld
import random

# Script to test joint limits.
if __name__ == "__main__":
  env = RCareWorld()

  person = env.create_human(id=100, name="Person",  is_in_scene=True)

  for _ in range(10000):
    lower1, upper1 = random.uniform(-50, 0), random.uniform(1, 50)
    lower2, upper2 = random.uniform(-50, 0), random.uniform(1, 50)
    lower3, upper3  = random.uniform(-50, 0), random.uniform(1, 50)

    person.setJointLimits("LeftUpperArm", lower1, upper1)
    person.setJointLimits("LeftHand", lower2, upper2, "X")
    person.setJointLimits("RightHand", lower3, upper3, "Z")

    print("Setting joint limits to:\n\tLeftUpperArm: ", lower1, upper1, "\n\tLeftHand: ", lower2, upper2, "\n\tRightHand: ", lower3, upper3, "\n\n")

    env.step()
