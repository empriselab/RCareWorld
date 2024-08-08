.. _Complete Guide to Environment Setup and Code Submission Using Docker:

EvalAI Submission Guide
====================================================================

Download and Install Docker
---------------------------

1. Go to Docker website download page: `Docker Hub <https://docs.docker.com/get-docker/>`_

2. Choose the appropriate installer for your operating system and follow the installation instructions provided on the site. 

Setting Up Your Docker Environment: We provide an example of how the code should be structured and how to 
set up the dockerfile in the `template folder <https://github.com/empriselab/RCareWorld/tree/phy-robo-care/template>`.
A sample Dockerfile looks like the one in `this link <https://github.com/empriselab/RCareWorld/blob/phy-robo-care/template/dockerfile>`.
You can use this as a reference to set up your Docker environment.

.. If you are participating in only 1 track, you should write one script that runs your entire codebase. For example,
.. if your entry-point script is `test_bathing.py`, you should write a Dockerfile that copies this script into the container and runs it.
.. If you are participating in both of the tracks, you should write two scripts, one for each track, and write a Dockerfile that copies both scripts into the container and runs them.

Build Your Docker
-----------------

1. Clone the GitHub repository and checkout the specific branch

.. code-block:: bash

    git clone https://github.com/empriselab/RCareWorld.git
    cd RCareWorld
    git checkout phy-robo-care
    cd template/docker-template

2. Run the Docker script

.. code-block:: bash

    sudo bash ./run_docker.sh

The `run_docker.sh` script will build the Docker image, run the container, and save the generated ZIP file.



Writing and Testing Code Inside Docker
--------------------------------------

.. code-block:: bash

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
    docker save your-image-name > your-image-name.tar

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

    evalai push rcareworld-final:latest --phase <phase_id>

5. If uploading directly, select the tar file and upload:

.. code-block:: none

    # Choose the file
    # Click on 'Upload File' button

You should expect to see your submission in the leaderboard after a while. This might take 10minutes to several hours depending on the size of the file and the number of submissions in the queue.
