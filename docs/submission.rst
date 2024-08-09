EvalAI Submission Guide
========================

This document provides a step-by-step guide on how to submit your code to the EvalAI platform for the PhyRC challenge on an Ubuntu computer.

Download and Install Docker
---------------------------

1. Visit the `Docker Download Page <https://docs.docker.com/get-docker/>`_.
2. Select the appropriate installer for Ubuntu and follow the provided installation instructions.

Set Up Your Docker Environment
------------------------------

We provide an example of how the code should be structured and how to set up the Dockerfile in the `template folder <https://github.com/empriselab/RCareWorld/tree/phy-robo-care/template>`_.

A sample Dockerfile can be found `here <https://github.com/empriselab/RCareWorld/blob/phy-robo-care/template/docker-template/dockerfile>`_. Use this as a reference to set up your Docker environment.

The Dockerfile runs ``run_python.shell`` to execute the code. If you are submitting for only one track, modify ``run_python.shell`` to include only the Python script for that track.

Ensure you have the codebase installed on your local machine by following the instructions in the `README.md file <https://github.com/empriselab/RCareWorld/tree/phy-robo-care?tab=readme-ov-file#here-is-the-code-for-rcareworld-phyrc-challenge->`_.

Build Your Docker Image
-----------------------

1. Navigate to the ``docker-template`` folder:

   .. code-block:: bash

      cd RCareWorld/template/docker-template

2. Run the Docker script:

   .. code-block:: bash

      sudo bash ./run_docker.shell

   The ``run_docker.sh`` script will build the Docker image and run the container.

   After the script completes, it will automatically enter Docker's interactive exec environment. You can explore the Docker operating environment to build your own Docker container. By default, the Docker container will continue running in detached mode. If you don't need it, you can manually stop it by typing `exit`` in the Docker shell.

    To prevent the Docker container from running indefinitely in the background, you can remove the last line `docker exec -it $CONTAINER_ID /bin/bash` from the `run_docker.shell`` script.

    If you don't want the Docker container to keep running after the process finishes, you can remove the last line `sleep infinity`` from the `run_python.shell`` script. This will automatically shut down the Docker container once the docker build and docker run processes are completed.

Write and Test Code Inside Docker
---------------------------------

1. Check the Docker container's ID (run this before entering the Docker environment):

   .. code-block:: bash

      docker ps

   This command displays information about the running Docker containers. Containers built with ``run_docker.sh`` or ``save_docker.sh`` will run in the background by default.

2. Access your Docker container's shell:

   .. code-block:: bash

      docker exec -it <container_id> bash

3. Navigate to the project directory:

   .. code-block:: bash

      cd /app/RCareWorld

4. Run your script (e.g., ``test_bathing.py``):

   .. code-block:: bash

      python test_bathing.py

   **Note:** If running code in the Docker container, ensure you have set ``graphics=False`` in ``RCareWorld()`` before copying your code.

Package Your Docker Environment
-------------------------------

1. Run the packaging script:

   .. code-block:: bash

      bash ./save_docker.shell

   The ``save_docker.shell`` script will build the Docker image, run the container, and generate a ZIP file.

   Like ``run_docker.shell``, ``save_docker.shell`` starts a Docker container that runs in the background by default. To save memory, the script removes the running Docker container after packaging. You can comment out the relevant statements to disable this behavior if preferred.

2. Alternatively, you can manually package your Docker image:

   .. code-block:: bash

      # Find your Docker image ID
      docker images

      # Use the image ID to package your Docker image:
      docker save <image_id> -o your_docker_name.tar

      # Create a directory to unpack the tar file
      mkdir unpacked_docker

      # Unpack the tar file into the directory
      tar -xf your_docker_name.tar -C unpacked_docker

      # Compress the unpacked files into a zip file
      zip -r your_docker_name.zip unpacked_docker

      # Clean up the unpacked directory and the original tar file
      rm -rf unpacked_docker
      rm your_docker_name.tar

   After packaging, submit the compressed ``.zip`` file.

   **Note:** You can also upload a ``.tar`` file directly. However, we recommend packaging in ``.zip`` format. We accept and evaluate both ``.tar`` and ``.zip`` files, but other file types will not be accepted and will receive a score of zero even if uploaded successfully.

Uploading to EvalAI
-------------------

1. Visit the `EvalAI Challenge Page <https://eval.ai/web/challenges/challenge-page/2351/overview>`_ and click on the 'Participate' button. Sign up or log in to your EvalAI account.
2. Select ``Phase 1``.
3. Choose the upload method depending on the file size:

   - Use CLI for file size > 400MB
   - Upload directly if file size < 400MB

4. If using the CLI, upload with:

   .. code-block:: bash

      pip install "evalai"

   Then, visit the `submission page <https://eval.ai/web/challenges/challenge-page/2351/my-submission>`_ and follow the instructions to submit your code. Each person’s token and submission command will differ, so copy the command from the webpage to submit.

5. If uploading directly, select the ``.zip`` or ``.tar`` file and upload:

   .. code-block:: none

      # Choose the file
      # Click on the 'Upload File' button

   Your submission should appear on the leaderboard after processing, which may take anywhere from 10 minutes to several hours depending on the file size and the number of submissions in the queue.
