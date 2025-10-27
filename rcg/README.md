# RCareGen

Robot control generation framework for RCareWorld simulation environment.

## Architecture

### Call Flow

```
User Input → main.py/test.py → KinovaTestEnv → LLMController → Unity
                                     ↓               ↓
                                  TCP:5004      OpenAI API
                                     ↓               ↓
                                Unity Scene    Robot Functions
```

### Data Flow Example

```
"Move to the cube" → Gradio chat → LLM processes command
    ↓
GPT-4 calls: move_to_object(name="cube")
    ↓
Find cube position → Calculate target → robot.IKTargetDoMove()
    ↓
Unity executes → Camera updates → Gradio shows result
```

## Installation

```bash
# Clone and install dependencies
cd rcg
pip install gradio pillow openai

# Install pyrcareworld
cd ../pyrcareworld
pip install -e .

# Set OpenAI API key
export OPENAI_API_KEY="sk-your-key"
```

## Usage

### Test Mode

Creates test scene with robot + 2 boxes:

```bash
# Web interface at http://localhost:7860
python -m rcg.test

# Terminal only
python -m rcg.test --no-gradio

# Custom port
python -m rcg.test --gradio-port 8080
```

### Production Mode

Connect to custom Unity scene:

```bash
# Configure IDs in env.py first
python -m rcg.main
```

## Project Structure

```
rcg/
├── env.py       # Unity environment wrapper
├── llm.py       # LLM controller and robot functions
├── prompt.py    # System prompts and function schemas
├── gradio.py    # Web interface
├── main.py      # Production entry point
└── test.py      # Test environment
```

## Configuration

### Unity Object IDs

Find IDs in Unity Inspector → RFUniverse Attr → Instance ID:

```python
# rcg/env.py
class KinovaTestEnv(RCareWorld):
    _kinova_id: int = 123456
    _gripper_id: int = 1234560
    _camera_id: int = 888888
```

### Adding Robot Functions

1. Define function in `llm.py`:

```python
def rotate_robot(x: float = 0, y: float = 0, z: float = 0) -> Dict:
    _global_robot.IKTargetDoRotate(rotation=[x, y, z], duration=2.0)
    _global_robot.WaitDo()
    return {"success": True, "message": f"Rotated to [{x}, {y}, {z}]"}
```

2. Add schema in `prompt.py`:

```python
{
    "name": "rotate_robot",
    "description": "Rotate robot end-effector",
    "parameters": {
        "type": "object",
        "properties": {
            "x": {"type": "number", "description": "X rotation"},
            "y": {"type": "number", "description": "Y rotation"},
            "z": {"type": "number", "description": "Z rotation"}
        },
        "required": ["x", "y", "z"]
    }
}
```

3. Register in `execute_function()`:

```python
if function_name == "rotate_robot":
    return rotate_robot(**arguments)
```

### Customizing Interface

Modify `gradio.py`:

```python
# Add home button
btn_home = gr.Button("🏠 Home", variant="primary")
btn_home.click(fn=go_home, outputs=btn_status)

def go_home() -> str:
    _global_robot.IKTargetDoMove([0, 0.5, 0.5], duration=2.0)
    _global_robot.WaitDo()
    return "✓ Home"
```

## API Reference

### KinovaTestEnv

```python
env = KinovaTestEnv(
    executable_file="@editor",  # Connect to Unity Editor
    graphics=True,
    port=5004
)

robot = env.get_kinova()
gripper = env.get_gripper()
camera = env.get_camera()
env.step(n)  # Execute n physics steps
```

### LLMController

```python
llm.initialize(env, robot, gripper)
controller = llm.LLMController()

result = controller.process_command("Move to cube")
# Returns: {"success": bool, "llm_response": str, "function_result": dict}
```

### Robot Functions

#### get_info(name=None)
Returns scene objects and positions.

#### move_to_object(name, offset_x=0, offset_y=0.1, offset_z=0)
Move to object with offset.

#### move_to_position(x, y, z, relative=False)
Move to absolute or relative position.

#### grasp_object(name, approach_height=0.5, lift_height=0.5)
Execute grasp sequence: approach → descend → grasp → lift.

#### release_object(lift_before_release=True)
Release grasped object.

## Troubleshooting

### Connection Failed
- Check Unity Editor is in Play mode
- Verify port 5004 is available
- Check object IDs match Unity scene

### API Errors
```bash
export OPENAI_API_KEY="sk-your-key"
```

### Port Conflict
```bash
python -m rcg.test --gradio-port 8080
```

### Robot Not Moving
- Check Unity physics not paused
- Verify robot has ControllerAttr component
- Test: `robot.IKTargetDoMove([0, 0.5, 0.5], 2.0)`

## Example Commands

```
"Show all objects"
"Move to the box"
"Move 20cm above left box"
"Grasp the box"
"Move up 30cm"
"Release object"
```

Control buttons:
- ⬆️⬇️⬅️➡️ 10cm movements
- 🤏 Close gripper
- 🖐️ Open gripper