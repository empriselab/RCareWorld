# Curobo with RCareWorld Installation Guide

curobo with rcareworld - [phyrc branch]

```bash
# install rcareworld
conda create -n rcareworld python=3.10
conda activate rcareworld
cd RCareWorld
git lfs install
git lfs pull
cd pyrcareworld
pip install -r requirements.txt
pip install -e .
pip uninstall numpy
conda install numpy

# install curobo
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
git clone https://github.com/NVlabs/curobo.git
cd curobo
pip install -e . --no-build-isolation
conda install -c conda-forge ninja libstdcxx-ng

# check curobo
python3 -m pytest . > pytest_results.log 2>&1
# Check the output log against install-pytest_output_reference.log. The reference log shows successful execution with some warnings but no errors.

# consistency diffusion
pip install h5py
```
