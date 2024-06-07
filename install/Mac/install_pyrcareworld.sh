#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda create -y --name rcareworld python=3.8 pip
conda activate rcareworld

brew install openssl
export LDFLAGS=“-L/opt/homebrew/opt/openssl@3/lib”
export CPPFLAGS=“-I/opt/homebrew/opt/openssl@3/include”
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1

brew install libomp

cd pyrcareworld
pip install -r requirements.txt
pip install -e .
cd ..
