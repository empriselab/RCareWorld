@echo off
REM Activate Conda environment
CALL %USERPROFILE%\miniconda3\Scripts\activate.bat

REM Create a new Conda environment
CALL conda create -y --name rcareworld python=3.8 pip

REM Activate the newly created environment
CALL conda activate rcareworld

REM Change to the project directory
cd pyrcareworld

REM Install Python dependencies
pip install -r requirements.txt
pip install -e .

REM Change back to the parent directory
cd ..
