from pyrcareworld.envs import RCareWorld
from pyrcareworld.attributes import sponge_attr
from pyrcareworld.attributes import cloth_score_attr
import random

# Script to test bed bathing in hackathon.
if __name__ == "__main__":
    env = RCareWorld()

    while True:
        score = cloth_score_attr.score_forces(env.instance_channel.data[250])
        print("Dressing Score: {}".format(score))

        env.step()
