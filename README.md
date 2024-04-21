![alt text](rcareworld.png)

# Here is the code for RCareWorld V1.0.0 🦾
- Check the website https://emprise.cs.cornell.edu/rcareworld/

We support Windows, Linux (Tested on Ubuntu), and MacOS. You need to make sure git and git-lfs is installed on your system. You should use powershell for windows, 
and bash for Linux and MacOS.
# Clone this repo
If you have ssh:
`git clone git@github.com:empriselab/RCareWorld.git`

otherwise,
`git clone https://github.com/empriselab/RCareWorld.git`

Checkout to the hackathon branch:
`git checkout hackathon`

Next, `git lfs pull`.

You should expect to see `Linux.zip`, `Mac.zip`, and `Windows.zip` under `hackathon_demo/Build/TestInstall` folder. Unzip the one that matches your system.


# Install guide
## Windows
Run `install/Windows/install_conda.bat`, and then run `install/Windows/install_pyrcareworld.bat`.
## Ubuntu
Run `install/Ubuntu/install_conda.sh`, and then run `install/Ubuntu/install_pyrcareworld.sh`.

Example commands:
`bash  install/Ubuntu/install_pyrcareworld.sh`

## Mac
Run `install/Mac/install_conda.sh`, and then run `install/Mac/install_pyrcareworld.sh`.