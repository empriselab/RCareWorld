#!/usr/bin/env bash -l
source ~/miniconda3/etc/profile.d/conda.sh
conda create -y --name rcareworld python=3.8 pip
source activate rcareworld
cd pyrcareworld
pip install -r requirements.txt
pip install -e .
cd ..