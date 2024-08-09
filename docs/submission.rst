EvalAI Submission Guide
===========

This document provides a step-by-step guide on how to submit your code to the EvalAI platform for the PhyRC challenge on a Ubuntu computer.

Download and Install Docker
---------------------------

1. Go to the Docker website download page: `Docker Download Link <https://docs.docker.com/get-docker/>`_

2. Choose the appropriate installer for Ubuntu and follow the installation instructions provided on the site. 

Set Up Your Docker Environment
----------------------------------

We provide an example of how the code should be structured and how to set up the Dockerfile in the `template folder <https://github.com/empriselab/RCareWorld/tree/phy-robo-care/template>`_.
A sample Dockerfile looks like the one in `this link <https://github.com/empriselab/RCareWorld/blob/phy-robo-care/template/docker-template/dockerfile>`_.
You can use this as a reference to set up your Docker environment. 

The Dockerfile runs `run_python.shell` to run the code. If you are only submitting to one of the tracks, modify `run_python.shell` to include only the python script for that track

Make sure you have the codebase installed on your local machine following the instructions in the `README.md file <https://github.com/empriselab/RCareWorld/tree/phy-robo-care?tab=readme-ov-file#here-is-the-code-for-rcareworld-phyrc-challenge->`_.

Build Your Docker
-----------------

1. Navigate to the `docker-template` folder:

    .. code-block:: bash
        
        cd RCareWorld/template/docker-template

2. Run the Docker script:

    .. code-block:: bash

        sudo bash ./run_docker.shell

    The `run_docker.sh` script will build the Docker image, run the container.
    
    After the `run_docker.sh` script completes execution, it will automatically enter the Docker environment. You can familiarize yourself with the Docker operating environment to build your own Docker container! Specifically, the Docker container will automatically continue running in the background. If not needed, you can manually stop it. You can exit the Docker exec mode by typing "exit". To avoid this operation, you can remove the last line `docker exec -it $CONTAINER_ID /bin/bash` from the `run_docker.sh` script.

    If you don't want to keep the Docker container running in the background, remove the last line `sleep infinity` from the `run_python.shell` script. This way, the Docker container will automatically shut down after the `docker build` and `docker run` processes are completed.



Write and Test Code Inside Docker
--------------------------------------

    .. code-block:: bash

        # Check the Docker container's ID
        # This command will output information about the running Docker containers. When you use `run_docker.sh` or `save_docker.sh`, the Docker containers you build will run in the background by default. You can use this method to view the relevant information.
        docker ps

        # Access your Docker container's shell
        docker exec -it <container_id> bash

        # Navigate to the project directory
        cd /app/RCareWorld

        # Run your script
        # The script can be named as anything but we use test_bathing.py as an example
        python test_bathing.py

    If you want to run code in the docker container, make sure you have set `graphics=False`` in `RCareWorld()`` before copying your code.




Packaging Your Docker Environment
---------------------------------

    .. code-block:: bash

        bash ./save_docker.shell
        
    The `save_docker.shell` script will build the Docker image, run the container.and generated ZIP file.
    
    Similarly, the first part of save_docker.shell is identical to run_docker.shell, and it will also start a Docker container that runs in the background by default. However, in the latter part, to save memory, the running Docker container will be removed. You can freely choose to comment out the relevant statements to decide whether to enable or disable this behavior.
    
    You can also use the command line to package your files. We recommend packaging them in .zip format, but we also support .tar format. You can use the following command line to package Docker:

    First,  using the following command:

    .. code-block:: shell

        # Find your Docker image ID
        docker images

        # Then use the image ID to package your Docker image:
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

    After packaging, submit the compressed `.zip` file.

    If you find it troublesome, you can also directly upload a `.tar`` file. Considering the diversity of platforms, our `save_docker.shell` will save it as a `.zip`` file. We recognize and evaluate both types of compressed files. However, please note that we only accept `.tar`` and `.zip`` files; other file types cannot be uploaded. Even if the upload is successful, it will default to a score of zero!

Uploading to EvalAI
-------------------

1. Visit the submission page for the competition: `EvalAI overview Page <https://eval.ai/web/challenges/challenge-page/2351/overview>`_
And then, click on the 'Participate' button. Sign up or log in to your EvalAI account.

2. Select the `Phase 1`.

3. Choose the upload method depending on the file size:

    - Use CLI for file size > 400MB
    - Upload file directly if file size < 400MB

4. If using the CLI, upload with:

    .. code-block:: bash

        pip install "evalai"

    
    Then go to `submission page <https://eval.ai/web/challenges/challenge-page/2351/my-submission>`_. Each person's token and submission command will differ. Copy the command from the webpage to submit.


    

        

5. If uploading directly, select the zip/tar file and upload:

    .. code-block:: none

        # Choose the file
        # Click on 'Upload File' button

    You should expect to see your submission in the leaderboard after a while. This might take 10 minutes to several hours depending on the size of the file and the number of submissions in the queue.