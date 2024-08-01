.. PhyRC Challenge Document documentation master file, created by
   sphinx-quickstart on Wed Jul 31 18:51:59 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PhyRC Challenge 's documentation!
====================================================


![alt text](rcareworld.png)

# Here is the code for RCareWorld PhyRC Challenge 🦾

This codebase contains a minimal install of RCareWorld. You will have access to executables without the scenes for the competition. We will release the simulation environments for the robot-assisted dressing and bed bathing on Aug 1st.
- Check the website https://emprise.cs.cornell.edu/rcareworld/
- Auto-generated APIs: Please only refer to this document and the tutorial playlists if you are participating in the PhyRC challenge. Do not use the links in the main branch. https://emprise.cs.cornell.edu/rcareworld-doc/
- Discuss in the forum https://github.com/empriselab/RCareWorld/discussions
- Watch our presentation https://www.youtube.com/watch?v=mNy1cloWrP0


# Hardware requirements
We support Windows and Linux (Tested on Ubuntu). We do not guarantee it works on MacOS. You need to make sure git and git-lfs are installed on your system. You should use Git Bash if you have it (else Powershell) for Windows, 
and use bash for Linux and MacOS. 

We highly recommend using Ubuntu 20.04 system which will be used for evaluation. Please make sure your computer has at least 10GB free space before starting.



# Pre-Installation Guide

## Installing Git and Git Large File Storage

You can skip this step if you already have *git* and *git-lfs* installed on your system.

Installation for git-lfs: https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage.
## Installing Conda
Follow the [conda install guidance](https://docs.anaconda.com/miniconda/miniconda-install/) to install conda.

## Cloning the Repo
- Clone the repo:  If you have ssh key setup on GitHub use: `git clone git@github.com:empriselab/RCareWorld.git` otherwise, `git clone https://github.com/empriselab/RCareWorld.git`

- Checkout to the competition branch and pull the large files: Navigate to the `RCareWorld` repository using the cd command. Example command: `cd RCareWorld`. Checkout to the branch for this competition (this step might take a while since it contains large files): `git checkout phy-robo-care` Next, run `git lfs pull`.

- Unzip the executables: Navigate to the `demo/Build` folder. You should expect to see `Linux.zip`, `Mac.zip`, and `Windows.zip` under `demo/Build/TestInstall` folder. Unzip the one that matches your system. 

# Install Guide
If you are proceeding immediately after the "Cloning the Repo" step, navigate back to the RCareWorld directory.

- Navigate to `RCareWorld` folder: Example command: `cd ~/RCareWorld` (this command may vary depending on where your RCareWorld folder is).
- Install `pyrcareworld` module: the bash file creates and activates a conda environment called `rcareworld`, and then installs the pyrcareworld module and its dependencies in that conda environment: 
  - Ubuntu: `bash install/Ubuntu/install_pyrcareworld.sh`.
  - Windows: `./install/Windows/install_pyrcareworld.bat`. Note on Windows you may need to install Microsoft Visual C++ 14.0 or greater using Visual Studio Installer. If you are confused as to how to do this, reference this tutorial: https://www.youtube.com/watch?v=yBvxsw6OOw4.
  - MacOS: `bash install/Mac/install_pyrcareworld.sh`.


# Testing Installation
Navigate to the `RCareWorld` folder and then to the `demo` folder.

Inside the `demo` folder, you will find four files titled `test_install_linux.py`, `test_install_mac.py`, `test_install_mac_silicon.py`, and `test_install_windows.py`. In order to test the installation, use the following commands: 

First, activate the conda environment: `conda activate rcareworld`.

Run `python test_install_<system_name>.py`, replace <system_name> with `linux`, `windows`, `mac`, or `mac_silicon`. If you are using mac silicon, make sure you have run the following commands in the terminal before running this script:
`arch -x86_64 bash` if your shell is bash
or 
`arch -x86_64 zsh` if your shell is zsh.


If you have correctly installed based on the installation guide, then a Unity window should open up and the resulting image should appear.
![alt text](./Test_Install_Image.png)

# Tutorial Videos
Congratulations! Now you have RCareWorld installed. For more information about using the simulation, please watch our [playlist](https://www.youtube.com/playlist?list=PLR4mEXh9zalLtbGLbx2A5TmX9Niy-svqq) of tutorials, which will be continuously updated.