Usage Guide
===========

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

For more details, please see the `GitHub repository <https://github.com/empriselab/RCareWorld/>`_.

Submission Guide
================

Download and Install Docker
---------------------------

1. Go to the Docker website download page: `Docker Download Link <https://docs.docker.com/get-docker/>`_

2. Choose the appropriate installer for your operating system and follow the installation instructions provided on the site. 

Setting Up Your Docker Environment
----------------------------------

We provide an example of how the code should be structured and how to set up the Dockerfile in the `template folder <https://github.com/empriselab/RCareWorld/tree/phy-robo-care/template>`_.
A sample Dockerfile looks like the one in `this link <https://github.com/empriselab/RCareWorld/blob/phy-robo-care/template/dockerfile>`_.
You can use this as a reference to set up your Docker environment.

.. If you are participating in only one track, you should write one script that runs your entire codebase. For example,
.. if your entry-point script is `test_bathing.py`, you should write a Dockerfile that copies this script into the container and runs it.
.. If you are participating in both tracks, you should write two scripts, one for each track, and write a Dockerfile that copies both scripts into the container and runs them.

Build Your Docker
-----------------

1. Clone the GitHub repository and checkout the specific branch:

    .. code-block:: bash

        git clone -b phy-robo-care https://github.com/empriselab/RCareWorld.git
        cd RCareWorld
        cd template/docker-template

2. Run the Docker script:

    .. code-block:: bash

        sudo bash ./run_docker.sh

    The `run_docker.sh` script will build the Docker image, run the container, and save the generated ZIP file.

Writing and Testing Code Inside Docker
--------------------------------------

    .. code-block:: bash

        # Check the Docker container's ID
        docker ps

        # Access your Docker container's shell
        docker exec -it <container_id> bash

        # Navigate to the project directory
        cd /app/RCareWorld

        # Run your script
        # The script can be named as anything but we use test_bathing.py as an example
        python test_bathing.py

Packaging Your Docker Environment
---------------------------------

    .. code-block:: bash

        # Save your Docker container as an image
        docker commit <container_id> your-image-name

        # Export your Docker image to a tar file
        docker save your-image-name | gzip > your-image-name.tar.gz

Uploading to EvalAI
-------------------

1. Visit the submission page for the competition: `EvalAI overview Page <https://eval.ai/web/challenges/challenge-page/2351/overview>`_
And then, click on the 'Participate' button. Sign up or log in to your EvalAI account.

2. Select the phase.

3. Choose the upload method depending on the file size:

    .. code-block:: none

        - Use CLI for file size > 400MB
        - Upload file directly if file size < 400MB

4. If using the CLI, upload with:

    .. code-block:: bash

        pip install "evalai"

        evalai set_token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1MTE5NTk2MywianRpIjoiMGJlZjY5NzVhNWI4NDM0OWEyM2RiOTcxZDc0NjRiYzkiLCJ1c2VyX2lkIjo0NTE3NH0.lZ_wVxaKqfXxVu2I4KJfeh8vPHOBOn_9YaUSnaQCncM

        evalai challenge 2351 phase submit --file <submission_file_path> --large

        # Use --private or --public flag in the submission command to make the submission private or public respectively.
        # example: evalai challenge 2351 phase submit --file <submission_file_path> --large --private

5. If uploading directly, select the zip/tar file and upload:

    .. code-block:: none

        # Choose the file
        # Click on 'Upload File' button

    You should expect to see your submission in the leaderboard after a while. This might take 10 minutes to several hours depending on the size of the file and the number of submissions in the queue.

Additional Notes
----------------

- GPU is highly recommended for running the environment.
- If you want to use Windows, download it from drive and update the executable_file path. The drive includes a folder for Windows only.
- You can try to run `python pyrcareworld/pyrcareworld/demo/test_scene.py` and then you will get a window similar to the screenshot below! This indicates that the environment is set up correctly.

    .. image:: ../test_scene.png
       :align: center
       :alt: Screenshot of the test scene.

- `test_bathing.py` and `test_dressing.py` are in RCareWorld/template.
