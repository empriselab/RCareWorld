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



Write and Test Code Inside Docker
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

    If you want to run code in the docker container, make sure you have set `graphics=False`` in `RCareWorld()`` before copying your code.








Packaging Your Docker Environment
---------------------------------

    .. code-block:: bash

        bash ./save_docker.shell
        
    The `save_docker.sh` script will build the Docker image, run the container.and generated ZIP file.

    You can also use the command line to package your files. We recommend packaging them in .zip format, but we also support .tar format. You can use the following command line to package Docker:

    First,  using the following command:

    .. code-block:: shell

        # Find your Docker image ID
        docker images

        # Then use the image ID to package your Docker image:
        docker save <image_id> | gzip > your_docker_name.tar.gz
        zip your_docker_name.zip your_docker_name.tar.gz

    After packaging, submit the compressed file.

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