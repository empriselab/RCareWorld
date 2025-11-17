# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RCareWorld is a Unity-based robotic simulation platform with Python bindings for robot manipulation tasks. The repository consists of two main components:

1. **pyrcareworld** - Python library for controlling Unity simulations
2. **rcg** (RCareGen) - LLM-based robot control generation framework using Gradio interface

## Development Setup

### Installation

```bash
# Create conda environment
conda create -n rcareworld python=3.10
conda activate rcareworld

# Install pyrcareworld
cd pyrcareworld
pip install -r requirements.txt
pip install -e .

# Install RCareGen dependencies
cd ../rcg
pip install gradio pillow openai
```

### Running Tests

```bash
# Test pyrcareworld connection to Unity
cd pyrcareworld/pyrcareworld/demo/examples
python example_kinova_gen3_move.py

# Test RCareGen environment
cd ../../../rcg
python env.py

# Test RCareGen with Gradio interface
python test.py
```

### Running RCareGen

RCareGen requires Unity Editor in Play mode:

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run with Gradio interface (connects to Unity Editor on port 5004)
python -m rcg.test

# Production mode
python -m rcg.main
```

## Code Architecture

### pyrcareworld Package Structure

**Core Components:**
- `envs/base_env.py` - `RCareWorld` base class for all environments
  - Manages Unity process lifecycle and communication
  - Provides API for scene manipulation, object instantiation, and physics control
  - Communication via TCP using `RFUniverseCommunicator`
- `attributes/` - Object attribute classes corresponding to Unity components
  - `base_attr.py` - Base attribute class
  - `controller_attr.py` - Robot arm/gripper control (articulation, IK, joint control)
  - `camera_attr.py` - Camera rendering and image capture
  - `rigidbody_attr.py` - Physics objects
  - `gameobject_attr.py` - Basic Unity GameObjects
- `side_channel/` - Message passing infrastructure between Python and Unity
- `utils/` - Communication protocol and utilities

**Key Patterns:**
- All environments inherit from `RCareWorld` base class
- Objects accessed via `env.GetAttr(id)` using Unity Instance IDs
- Synchronous stepping: `env.step(count)` advances simulation
- Built-in assets available via `env.InstanceObject(name, id)`

### rcg (RCareGen) Architecture

**Files:**
- `env.py` - `KinovaTestEnv` wrapper around RCareWorld for Kinova robot
- `llm.py` - LLM controller with robot function implementations
- `prompt.py` - System prompts and OpenAI function schemas
- `gradio_ui.py` - Web interface for robot control
- `main.py` - Production entry point
- `test.py` - Development/testing entry point

**Data Flow:**
```
User Command → Gradio UI → LLMController.process_command()
                              ↓
                    OpenAI API (function calling)
                              ↓
                    execute_function() → Robot Functions
                              ↓
                    KinovaTestEnv → Unity via TCP (port 5004)
                              ↓
                    Camera Image + State → Gradio Display
```

**Unity Instance ID Configuration:**
RCareGen requires specific Instance IDs set in Unity Inspector (RFUniverse Attr component):
- Kinova Robot: `315893` (defined in `env.py:32`)
- Gripper: `3158930` (defined in `env.py:33`)
- Camera: `35181` (defined in `env.py:34`)
- Optional test objects: Banana1 (`111111`), Banana2 (`222222`), Banana3 (`333333`)

Objects must exist in Unity scene with matching IDs before Python can access them.

### Communication Protocol

**Python → Unity:**
- Commands sent via `communicator.send_object(type, *args)`
- Types: "Env", "Instance", "Debug", "Message", "Object"
- Synchronous step-based execution

**Unity → Python:**
- Data received in `_receive_data()` callback
- Parsed into `env.data` (environment state) and `env.attrs` (object attributes)
- Instance data automatically creates/updates attribute objects

## Adding Robot Functions to RCareGen

To add a new robot control function:

1. **Define function in `llm.py`:**
```python
def my_new_function(param1: float, param2: str) -> Dict:
    """Function that does something with the robot."""
    _global_robot.SomeMethod(param1)
    _global_robot.WaitDo()
    return {"success": True, "message": f"Did something with {param2}"}
```

2. **Add OpenAI schema in `prompt.py`:**
```python
FUNCTION_SCHEMAS = [
    # ... existing functions
    {
        "name": "my_new_function",
        "description": "Clear description of what this does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "number", "description": "What param1 does"},
                "param2": {"type": "string", "description": "What param2 does"}
            },
            "required": ["param1", "param2"]
        }
    }
]
```

3. **Register in `execute_function()` in `llm.py`:**
```python
def execute_function(function_name: str, arguments: Dict[str, Any]) -> Dict:
    if function_name == "my_new_function":
        return my_new_function(**arguments)
    # ... existing functions
```

4. **Update system prompt in `prompt.py`** to describe when to use the new function.

## Unity Object Instance IDs

When working with Unity scenes in RCareGen:
- Instance IDs are set in Unity Inspector → RFUniverse Attr component → Instance ID field
- Python code references these IDs as class attributes (e.g., `_kinova_id = 315893`)
- Use `env.GetAttr(id)` to access Unity objects from Python
- Objects detected by `get_info()` LLM function must be registered in `env.attrs`
- To add new objects: set Unity Instance ID → add getter method in `env.py` → call getter during initialization

## Common Commands

```bash
# Install pyrcareworld in development mode
cd pyrcareworld && pip install -e .

# Run RCareGen test interface
cd rcg && python test.py

# Run RCareGen production mode
cd rcg && python main.py

# Run single example
python pyrcareworld/pyrcareworld/demo/examples/example_kinova_gen3_move.py

# Test environment connection
python rcg/env.py
```

## Testing LLM Functions

After modifying LLM functions, test with:
```bash
cd rcg
python test.py  # Opens Gradio interface

# Or test specific functions:
python -c "
from rcg.env import KinovaTestEnv
import rcg.llm as llm

env = KinovaTestEnv()
robot = env.get_kinova()
gripper = env.get_gripper()
llm.initialize(env, robot, gripper)

result = llm.get_info()
print(result)
"
```

## Important Notes

- **Unity Editor Mode**: Use `executable_file="@editor"` to connect to Unity Editor instead of standalone build
- **Port Configuration**: Default port is 5004 for editor mode, 5005+ for standalone builds
- **Thread Safety**: RCareGen uses threading locks (`_unity_lock`) when integrating with Gradio to prevent race conditions
- **WaitDo() Pattern**: Robot commands are queued; call `robot.WaitDo()` to execute and wait for completion
- **IK vs Joint Control**: When `native_ik=True` in URDF loading, use `IKTargetDoMove/DoRotate`; when `False`, use `SetJoint*` methods
- **Object Detection**: For LLM to detect objects via `get_info()`, objects must be in `env.attrs` (either pre-existing with Instance IDs or instantiated via `env.InstanceObject()`)

## Project-Specific Conventions

- Python files use type hints extensively
- Robot control functions return `Dict` with `{"success": bool, "message": str, ...}`
- LLM system prompts are detailed and include usage examples
- Global references (`_global_env`, `_global_robot`, `_global_gripper`) allow robot functions to be stateless
- RCareGen separates concerns: `env.py` (Unity wrapper), `llm.py` (function logic), `prompt.py` (LLM interface), `gradio_ui.py` (UI)

## Documentation

- Website: https://emprise.cs.cornell.edu/rcareworld/
- ReadTheDocs: https://rcareworld.readthedocs.io/en/latest/
- Forum: https://github.com/empriselab/RCareWorld/discussions
- Presentation: https://www.youtube.com/watch?v=mNy1cloWrP0
