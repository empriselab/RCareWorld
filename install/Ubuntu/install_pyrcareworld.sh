#!/usr/bin/env bash -l
eval "$(conda shell.bash hook)"
conda create -y --name rcareworld python=3.8 pip
source activate rcareworld
cd pyrcareworld
pip install -r requirements.txt
pip install -e .
cd ..