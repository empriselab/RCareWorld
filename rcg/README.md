# RCareGen

LLM-based robot control interface for RCareWorld simulation environment.

## Quick Start

```bash
# Install dependencies
pip install gradio pillow openai

# Set API key (if using OpenAI)
export OPENAI_API_KEY="your-key"

# Run the interface
python -m rcg.main
```

Open your browser to `http://localhost:7860`

## Available Functions

### Core Functions

- **get_info(name=None)** - Get objects in scene with positions
- **move_to_object(name, offset_x=0, offset_y=0.1, offset_z=0)** - Move to object with offset
- **move_to_position(x, y, z, relative=False)** - Move to position (absolute or relative)
- **grasp_object(name, lift_height=0.5)** - Grasp object using magnetic attachment
- **release_object(lift_before_release=True, lift_height=0.1)** - Release grasped object

### Example Commands

```
"Show all objects"
"Move to banana 1"
"Grasp banana 3"
"Move up 20cm"
"Release object"
```

## Tutorial Resources

- **Tutorial Document**: [Google Drive](https://drive.google.com/file/d/1VT1G3hnBDoDD1Aq0behTHs4pGkSDrfb4/view?usp=drive_link)
- **Tutorial Video**: [Google Drive](https://drive.google.com/file/d/1FrahwT_PfV3H-C2helEX4lGFJ4gjyV_s/view?usp=drive_link)
- **Tutorial LLm Video**: [Google Drive](https://drive.google.com/file/d/1m96CK3HEdq-G2Hq9wozDHhkClZfo933W/view?usp=drive_link)

## Unity Setup

Set Instance IDs in Unity Inspector (RFUniverse Attr component):

**Required:**
- Kinova Robot: `315893`
- Gripper: `3158930`
- Camera: `35181`

**Optional (for testing):**
- Banana1: `111111`
- Banana2: `222222`
- Banana3: `333333`

## Project Structure

```
rcg/
├── env.py          # Unity environment wrapper
├── llm.py          # LLM controller and robot functions
├── prompt.py       # System prompts and function schemas
├── gradio_ui.py    # Web interface
└── main.py         # Entry point
```

## Configuration

Edit `rcg/env.py` to set Unity object IDs:

```python
class KinovaTestEnv(RCareWorld):
    _kinova_id: int = 315893
    _gripper_id: int = 3158930
    _camera_id: int = 35181
```

## Adding New Functions

1. **Define function** in `llm.py`:
```python
def my_function(param: float) -> Dict:
    _global_robot.DoSomething(param)
    _global_robot.WaitDo()
    return {"success": True, "message": "Done"}
```

2. **Add schema** in `prompt.py` to `FUNCTION_SCHEMAS`

3. **Register** in `FUNCTION_MAP` in `llm.py`
