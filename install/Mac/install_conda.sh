#!/bin/bash
# Ensuring the directory for Miniconda installation exists
mkdir -p ~/miniconda3
curl -L "https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh" -o ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
