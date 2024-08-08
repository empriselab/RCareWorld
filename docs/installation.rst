Installation Guide
==================

This guide provides instructions for both local testing and Docker-based setup.

Local Testing
-------------

1. Clone the GitHub repository and checkout the `phy-robo-care` branch:

    .. code-block:: bash

        git clone -b phy-robo-care https://github.com/empriselab/RCareWorld.git

2. Install the necessary libraries before running:

    .. code-block:: bash

        sudo apt-get update
        sudo apt-get install libassimp-dev libopenblas-dev liblapack-dev

3. Install Python dependencies:

    .. code-block:: bash

        # Install conda if not already installed
        # Follow instructions from https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html

        # Create a conda environment with Python 3.10
        conda create -n rcareworld python=3.10

        # Activate the conda environment 
        conda activate rcareworld

        # Install the requirements
        cd pyrcareworld
        pip install -r requirements.txt
        pip install -e .
        pip install upgrade open3d

4. Install the NVIDIA driver if you have a GPU or ensure your computer can run smoothly even without a GPU. You can download the NVIDIA drivers from the official `NVIDIA website <https://www.nvidia.com/Download/index.aspx>`_.

5. Run examples for testing:

    .. code-block:: bash

        # Verify the installation works
        cd pyrcareworld/demo/examples
        python test_scene.py

6. Test specific scripts:

    .. code-block:: bash

        cd /RCareWorld/template
        python test_bathing.py
        python test_dressing.py
