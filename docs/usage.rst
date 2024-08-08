EvalAI Submission Guide
===========

Download and Install Docker
---------------------------

1. Go to the Docker website download page: `Docker Download Link <https://docs.docker.com/get-docker/>`_

2. Choose the appropriate installer for your operating system and follow the installation instructions provided on the site. 

Set Up Your Docker Environment
----------------------------------

We provide an example of how the code should be structured and how to set up the Dockerfile in the `template folder <https://github.com/empriselab/RCareWorld/tree/phy-robo-care/template>`_.
A sample Dockerfile looks like the one in `this link <https://github.com/empriselab/RCareWorld/blob/phy-robo-care/template/docker-template/dockerfile>`_.
You can use this as a reference to set up your Docker environment.

Build Your Docker
-----------------

1. Clone the GitHub repository and checkout the specific branch:

    .. code-block:: bash

        git clone -b phy-robo-care https://github.com/empriselab/RCareWorld.git
        cd RCareWorld
        cd template/docker-template

2. Run the Docker script:

    .. code-block:: bash

        # The run_docker.sh script is in the template/docker-template folder
        sudo bash ./run_docker.sh

    The `run_docker.sh` script will build the Docker image, run the container, and save the generated ZIP file.

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

2. Select the `Dev Phase`_.

3. Choose the upload method depending on the file size:

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