![alt text](rcareworld.png)

# Here is the code for RCareWorld V1.0.0 🦾
- Check the website https://emprise.cs.cornell.edu/rcareworld/
- Auto-generated APIs https://emprise.cs.cornell.edu/rcareworld-doc/

We support Windows, Linux (Tested on Ubuntu), and MacOS. You need to make sure git and git-lfs are installed on your system. You should use Git Bash if you have it (else Powershell) for windows, 
and use bash for Linux and MacOS. 

Please make sure your computer has enough (at least 5GB) free space before starting.

# Pre-Installation Guide

## Installing Git and Git Large File Storage

You can skip this step if you already have git and git-lfs installed on your system.

### Windows
Follow https://www.youtube.com/watch?v=JgOs70Y7jew for git installation on Windows.

### Linux
#### Fedora 
Use `sudo dnf install git-all`
#### Debian-Based Distribution (Ubuntu)
Use `sudo apt install git-all`
#### Other options
Reference https://git-scm.com/download/linux

### Mac
Follow https://www.youtube.com/watch?v=Mf3l8z6oxQ0 for git installation on Mac.

### Git Large File Storage
Installation for git-lfs on all OS systems can be found here: https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage.

## Cloning the Hackathon Repo

Open up Terminal, Git Bash, or Powershell depending on the Operating System your computer is using.

If you have ssh key setup on github use:
`git clone git@github.com:empriselab/RCareWorld.git`

otherwise,
`git clone https://github.com/empriselab/RCareWorld.git`

Navigate to the `RCareWorld` repository using the cd command.
Example command: `cd RCareWorld`

Checkout to the hackathon branch:
`git checkout hackathon`

Next, `git lfs pull`.

Then navigate to `TestInstall` folder which is in `hackathon_demo` folder.

You should expect to see `Linux.zip`, `Mac.zip`, and `Windows.zip` under `hackathon_demo/Build/TestInstall` folder. Unzip the one that matches your system.

# Install Guide

If you are preceeding immediately after the "Cloning the Hackathon Repo" step, navigate back to the RCareWorld directory.
Example commands: `cd ~/RCareWorld`

If you already have anaconda installed on your system, skip installing `install_conda`. 

## Windows
Run `install/Windows/install_conda.bat`, and then run `install/Windows/install_pyrcareworld.bat`.

Example commands:
`./install/Windows/install_pyrcareworld.bat`

Note on Windows you may need to install Microsoft Visual C++ 14.0 or greater using Visual Studio Installer.
If you are confused as to how to do this, reference this tutorial: https://www.youtube.com/watch?v=yBvxsw6OOw4.

## Ubuntu
Run `install/Ubuntu/install_conda.sh`, and then run `install/Ubuntu/install_pyrcareworld.sh`.

Example commands:
`bash install/Ubuntu/install_pyrcareworld.sh`

## Mac
Run `install/Mac/install_conda.sh`, and then run `install/Mac/install_pyrcareworld.sh`.

Example commands:
`bash install/Mac/install_pyrcareworld.sh`. 

# Testing Installation
Navigate to the `RCareWorld` folder and then to the `hackathon_demo` folder.

Inside the `hackathon_demo` folder, you will find four files titled `test_install_linux.py`, `test_install_mac.py`, `test_install_mac_silicon.py`, and `test_install_windows.py`. In order to test installation, use the following commands: 

First activate the conda environment: `conda activate rcareworld`.

## Windows
Run `python test_install_windows.py`.

## Linux
Run `python test_install_linux.py`.

## Mac
### Intel
Run `python test_install_mac.py`.
### Apple Silicon
Run `python test_install_mac_silicon.py`.
### Don't know if Intel or Apple Silicon
It is necessary that you run the correct test. If you do not know whether you have Apple Silicon or Intel, please reference this site https://www.sweetwater.com/sweetcare/articles/intel-based-mac-or-mac-with-apple-silicon/.

## Test Result
If you have correctly installed based on the installation guide, then a Unity window should open up and the resulting image should appear.
![alt text](Test_Install_Image.png)
