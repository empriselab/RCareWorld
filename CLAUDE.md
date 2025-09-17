# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

RCareWorld is a robotics simulation environment for physical robot care research, specifically designed for the PhyRC Challenge. The codebase consists of:

- **Unity Engine Integration**: Communicates with Unity-based simulation environments via TCP/socket connections
- **Python Interface (`pyrcareworld`)**: Main package providing Python bindings and environment wrappers
- **Task-Specific Environments**: Bathing and dressing simulation environments with scoring systems
- **Template Scripts**: Ready-to-use examples in the `template/` directory
- **Diffusion Policy Integration**: Training diffusion policy models on RCareWorld data

## Development Commands

### Environment Setup
```bash
# Create conda environment
conda create -n rcareworld python=3.10
conda activate rcareworld

# Install dependencies and package
cd pyrcareworld
pip install -r requirements.txt
pip install -e .

# Fix numpy compatibility for open3d
pip uninstall numpy
conda install numpy

# Optional: Install OMPL for motion planning
python3 -m pip install https://github.com/ompl/ompl/releases/download/prerelease/ompl-1.6.0-cp310-cp310-manylinux_2_28_x86_64.whl
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test modules
pytest tests/test_base_env.py
pytest tests/test_bathing_env.py
pytest tests/test_ompl.py

# Test installation (note: test_scene.py mentioned in README doesn't exist)
cd pyrcareworld/demo/examples
python example_rl.py  # or any other example script
```

### Running Examples
```bash
# Starter scripts (headless by default)
python template/test_bathing.py
python template/test_dressing.py

# With graphics rendering
python template/test_bathing.py --graphics
python template/test_dressing.py --graphics

# Demo examples
cd pyrcareworld/demo/examples
python example_rl.py
python example_ompl.py
```

### Diffusion Policy Training
```bash
# For bathing task diffusion policy training
conda activate robodiff
cd diffusion_policy
./train_bathing.sh

# Manual training command
PYTHONPATH=/cephfs/chenshuaixing/rcare/rcw/diffusion_policy python train.py --config-dir=. --config-name=bathing_diffusion_policy_cnn.yaml training.seed=42 training.device=cuda:0 hydra.run.dir='data/outputs/${now:%Y.%m.%d}/${now:%H.%M.%S}_bathing_diffusion_policy'
```

## Architecture

### Core Components

1. **Base Environment (`pyrcareworld/envs/base_env.py`)**
   - `RCareWorld` class: Abstract base for all environments
   - Manages Unity executable communication via `RFUniverseCommunicator`
   - Handles scene loading, asset management, and rendering control
   - Supports both local and remote Unity instances

2. **Task Environments**
   - `BathingEnv` (`pyrcareworld/envs/bathing_env.py`): Bathing assistance simulation
   - `DressingEnv` (`pyrcareworld/envs/dressing_env.py`): Clothing assistance simulation
   - Both extend base environment with task-specific attributes and scoring

3. **Attributes System (`pyrcareworld/attributes/`)**
   - Modular components for different simulation objects
   - `BaseAttr`: Foundation class for all simulation attributes
   - Specific attributes: `humanbody_attr`, `cloth_attr`, `camera_attr`, etc.

4. **Communication Layer (`pyrcareworld/utils/rfuniverse_communicator.py`)**
   - TCP socket communication with Unity
   - Side channels for custom message passing
   - Supports both local and remote Unity instances

5. **Diffusion Policy Integration (`diffusion_policy/`)**
   - Training diffusion policy models on RCareWorld bathing data
   - Custom dataset class for bathing data with 96x96 RGB images + 13-dim robot state
   - 7-DOF robot action space with diffusion U-Net hybrid policy
   - Checkpoint storage in `data/outputs/` with wandb logging support

### Key Patterns

- **Attribute-Based Architecture**: Objects in simulation are composed of attributes that define their capabilities
- **Unity Integration**: Python acts as controller, Unity handles physics and rendering
- **Environment Wrappers**: Gym-compatible interfaces for RL integration
- **Asset Management**: Pre-loading and lazy loading of 3D assets and scenes
- **Zarr Data Format**: Used for efficient storage of training data with compression

### Configuration

- User config stored in `~/.rcareworld/config.json`
- Contains paths to Unity executables and asset directories
- Scene files located in `<PlayerName>_Data/StreamingAssets/SceneData/`
- Scores saved to `~/.config/unity3d/RCareWorld/DressingPlayer/`
- Diffusion policy configs in `diffusion_policy/config/` using Hydra framework

### Testing Structure

- Unit tests in `tests/` directory using pytest
- Integration tests verify Unity communication
- Example scripts serve as functional tests
- CI runs tests in headless mode on Ubuntu 20.04
- Specific tests for bathing motions: `test_bathing_wash_upper.py`, `test_bathing_dry_upper.py`, etc.

## Important Notes

- Unity executable must be available for full functionality
- Graphics mode requires display (use `--graphics` flag for local testing)
- Memory usage can be high for dressing scenes
- Port 5004 is default for Unity communication (configurable)
- Git LFS is used for large binary assets
- Diffusion policy training requires GPU and ~8-12GB GPU memory
- Known dependency issue with `huggingface_hub` compatibility fixed in diffusers 0.11.1