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

1. Clone the GitHub repository and enter the template folder:

    .. code-block:: bash
        
        cd RCareWorld/template/docker-template

2. Run the Docker script:

    .. code-block:: bash

        # The run_docker.sh script is in the template/docker-template folder
        sudo bash ./run_docker.shell

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

        bash ./save_docker.shell

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

    
    Then go to `https://eval.ai/web/challenges/challenge-page/2351/submission`_ . Each person's token and submission command will differ. Copy the command from the webpage to submit.

    

        

5. If uploading directly, select the zip/tar file and upload:

    .. code-block:: none

        # Choose the file
        # Click on 'Upload File' button

    You should expect to see your submission in the leaderboard after a while. This might take 10 minutes to several hours depending on the size of the file and the number of submissions in the queue.