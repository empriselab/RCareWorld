![alt text](rcareworld.png)
# Here is the code for RCareWorld PhyRC Challenge 🦾
This codebase requires a minimal installation of RCareWorld. You will have access to executables without the scenes for the competition. We will release the simulation environments for the robot-assisted dressing and bed bathing before Aug 8th AOE.

This repo is currently in the testing stage.
- Check the website https://emprise.cs.cornell.edu/rcareworld/
- APIs: Please only refer to this document if you are participating in the PhyRC challenge. Please don't use the links in the main branch. https://rcareworld.readthedocs.io/en/phy-robo-care/
- Discuss in the forum https://github.com/empriselab/RCareWorld/discussions


# Hardware requirements
While RCareWorld supports Linux, Windows, and Mac (experimental), our evaluation platform is based on Ubuntu 20.04. We do not guarantee the simulation environments for the competition work on MacOS, Windows, or other Linux versions as intended. The executable files are by default for Linux systems. If you want to use Windows or Mac (not recommended), download it from [drive](https://drive.google.com/drive/folders/1TW-C6k1z5xCdgE7q1ht3Flb2FaeCrQ51?usp=sharing) and update the executable_file path.

We highly recommend using an Ubuntu 20.04 system which will be used for evaluation. Please make sure your computer has at least 10GB of free space before starting.

# Download Guide
- Clone the repo: `git clone https://github.com/empriselab/RCareWorld.git`
- Switch to the `phy-robo-care` branch: `cd RCareWorld` and then `git checkout phy-robo-care `

# Install Guide
- Create a conda environment with Python 3.10: `conda create -n rcareworld python=3.10`
- Install the requirements: `cd pyrcareworld` and then `pip install -r requirements.txt`
- Install pyrcareworld: `pip install -e .`

# Get Started with the Examples
Check the examples in `pyrcareworld/pyrcareworld/demo/examples` folder. 

# Starter Scripts for Bathing and Dressing Tasks
Check the `test_bathing.py` and `test_dressing.py` to get an overall idea about how to use the simulation environments. Your score will be 
stored in a json file called `spongeScore.json` for bathing and `dressingScore.json` for dressing under `~/.config/unity3d/RCareWorld/RCareWorld/`
