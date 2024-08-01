.. _Complete Guide to Environment Setup and Code Submission Using Docker:

Complete Guide to Environment Setup and Code Submission Using Docker
====================================================================

Download and Install Docker
---------------------------

1. Visit the official Docker website download page: `Docker Hub <https://hub.docker.com/>`_

2. Choose the appropriate installer for your operating system and follow the installation instructions provided on the site.

Setting Up Your Docker Environment
----------------------------------

.. code-block:: bash

    # Create a Dockerfile in your project directory
    FROM python:3.10-slim
    WORKDIR /app
    RUN apt-get update && apt-get install -y git curl
    RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
    RUN apt-get install -y git-lfs && git lfs install
    RUN git clone https://github.com/empriselab/RCareWorld.git
    WORKDIR /app/RCareWorld
    RUN git checkout phy-robo-care
    RUN git lfs pull
    COPY requirements.txt /app/RCareWorld/
    RUN pip install --no-cache-dir -r requirements.txt
    COPY test_bathing.py /app/RCareWorld/
    CMD ["python", "test_bathing.py"]

3. Build the Docker image

.. code-block:: bash

    docker build -t rcareworld-environment .

4. Run your Docker container

.. code-block:: bash

    docker run -it rcareworld-environment

Writing and Testing Code Inside Docker
--------------------------------------

.. code-block:: bash

    # Access your Docker container's shell
    docker exec -it <container_id> bash

    # Navigate to the project directory
    cd /app/RCareWorld

    # Run your script
    python test_bathing.py

Packaging Your Docker Environment
---------------------------------

.. code-block:: bash

    # Save your Docker container as an image
    docker commit <container_id> rcareworld-final

    # Export your Docker image to a tar file
    docker save rcareworld-final > rcareworld-final.tar

Uploading to EvalAI
-------------------

1. Visit the submission page for the competition: `EvalAI Submission Page <https://eval.ai/web/challenges/challenge-page/2351/submission>`_

2. Select the appropriate phase as shown in the provided image.

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

This guide should help you through the entire process from environment setup to code submission using Docker. The steps include all necessary commands and should ensure a smooth workflow and successful submission on EvalAI.
