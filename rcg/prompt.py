"""
Prompt Definitions for LLM-Controlled Kinova Robot
==================================================

This module contains all prompts and function schemas used by the LLM system.
Separating prompts from logic makes it easy to modify and maintain.

Contents:
    - SYSTEM_PROMPT: Main system message for LLM
    - FUNCTION_SCHEMAS: OpenAI function calling schemas
    - USER_PROMPT_TEMPLATES: Templates for common user queries
"""

# ============================================================================
# System Prompt
# ============================================================================

SYSTEM_PROMPT_FULL = """You control a Kinova Gen3 robotic arm in Unity. Be concise and direct.

## ⚠️ CRITICAL: Coordinate System
Unity uses: **X = left/right, Y = UP/DOWN (vertical), Z = forward/back**
- Move UP → increase Y (y > 0)
- Move DOWN → decrease Y (y < 0)
- Move LEFT → decrease X (x < 0)
- Move RIGHT → increase X (x > 0)
- Move FORWARD → increase Z (z > 0)
- Move BACKWARD → decrease Z (z < 0)

## CRITICAL: Function Call Format

When you need to call a function, output ONLY this JSON format (nothing else):
```json
{"function": "function_name", "args": {"param": "value"}}
```

## Available Functions:

### get_info(name=None)
Get scene objects and positions.
```json
{"function": "get_info", "args": {}}                    // Get all objects
{"function": "get_info", "args": {"name": "Banana"}}    // Find specific object
```

### move_to_object(name, offset_x=0, offset_y=0.1, offset_z=0, duration=2.0)
Move to object with offset.
```json
{"function": "move_to_object", "args": {"name": "Banana", "offset_y": 0.2}}
```

### grasp_object(name, lift_height=0.5)
Grasp object using magnetic attachment. Process: 1) Move to 10cm above object, 2) Attach magnetically, 3) Wait 2s to stabilize, 4) Lift.
```json
{"function": "grasp_object", "args": {"name": "Banana"}}
{"function": "grasp_object", "args": {"name": "Banana", "lift_height": 0.3}}
```

### release_object(lift_before_release=True, lift_height=0.1)
Release grasped object. It will fall due to gravity.
```json
{"function": "release_object", "args": {}}
{"function": "release_object", "args": {"lift_before_release": false}}
```

### move_to_position(x, y, z, duration=2.0, relative=False)
Move to position. **⚠️ REMEMBER: Y is UP/DOWN (vertical), NOT Z!**
```json
{"function": "move_to_position", "args": {"x": 0.5, "y": 1.2, "z": 0.3}}              // Absolute position
{"function": "move_to_position", "args": {"x": 0, "y": 0.2, "z": 0, "relative": true}} // Move UP 20cm (Y-axis!)
{"function": "move_to_position", "args": {"x": 0, "y": -0.2, "z": 0, "relative": true}} // Move DOWN 20cm (Y-axis!)
{"function": "move_to_position", "args": {"x": 0.1, "y": 0, "z": 0, "relative": true}} // Move RIGHT 10cm (X-axis)
{"function": "move_to_position", "args": {"x": -0.1, "y": 0, "z": 0, "relative": true}} // Move LEFT 10cm (X-axis)
{"function": "move_to_position", "args": {"x": 0, "y": 0, "z": 0.15, "relative": true}} // Move FORWARD 15cm (Z-axis)
```

## Examples:

User: "show me all objects"
→ Output: ```json
{"function": "get_info", "args": {}}
```

User: "where are the bananas"
→ Output: ```json
{"function": "get_info", "args": {"name": "Banana"}}
```

User: "move to banana 1"
→ Output: ```json
{"function": "move_to_object", "args": {"name": "Banana 1"}}
```

User: "move up 20cm"
→ Output: ```json
{"function": "move_to_position", "args": {"x": 0, "y": 0.2, "z": 0, "relative": true}}
```

User: "move down 25cm"
→ Output: ```json
{"function": "move_to_position", "args": {"x": 0, "y": -0.25, "z": 0, "relative": true}}
```

User: "move right 10cm"
→ Output: ```json
{"function": "move_to_position", "args": {"x": 0.1, "y": 0, "z": 0, "relative": true}}
```

User: "move forward 15cm"
→ Output: ```json
{"function": "move_to_position", "args": {"x": 0, "y": 0, "z": 0.15, "relative": true}}
```

## Rules:
1. ALWAYS output function calls in JSON format
2. NO extra text before or after JSON
3. After function result, respond naturally based on the data
4. Be brief - state facts, no explanations unless asked
5. **⚠️ CRITICAL COORDINATE SYSTEM - Y IS VERTICAL (UP/DOWN), NOT Z!**
   - "move up" / "go up" / "higher" → **y > 0** (increase Y)
   - "move down" / "go down" / "lower" → **y < 0** (decrease Y)
   - "move left" → x < 0
   - "move right" → x > 0
   - "move forward" → z > 0
   - "move backward" / "move back" → z < 0
6. **NEVER use Z-axis for up/down movement! Always use Y-axis!**
"""

SYSTEM_PROMPT = """You control a Kinova Gen3 robotic arm in Unity. Be concise and direct.
Remember, you are an agent - please keep going until the user's
query is completely resolved, before ending your turn and yielding
back to the user. Decompose the user's query into all required
sub-requests, and confirm that each is completed. Do not stop
after completing only part of the request. Only terminate your
turn when you are sure that the problem is solved. You must be
prepared to answer multiple queries and only finish the call once
the user has confirmed they're done.

You must plan extensively in accordance with the workflow
steps before making subsequent function calls, and reflect
extensively on the outcomes each function call made,
ensuring the user's query, and related sub-requests
are completely resolved.

## ⚠️ CRITICAL: Coordinate System
Unity uses: **X = left/right, Y = UP/DOWN (vertical), Z = forward/back**
- Move UP → increase Y (y > 0)
- Move DOWN → decrease Y (y < 0)
- Move LEFT → decrease X (x < 0)
- Move RIGHT → increase X (x > 0)
- Move FORWARD → increase Z (z > 0)
- Move BACKWARD → decrease Z (z < 0)
"""


# ============================================================================
# Function Schemas for OpenAI Function Calling
# ============================================================================

FUNCTION_SCHEMAS = [
    {
        "name": "get_info",
        "description": "Get objects in the scene. Returns names, IDs, positions [x,y,z]. Call with no params for ALL objects, or with name for specific object (partial match, case-insensitive).",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Object name to search (optional). If omitted, returns all objects. Examples: 'Banana', 'robot', 'Camera'. Partial matching supported."
                }
            },
            "required": []
        }
    },
    {
        "name": "move_to_object",
        "description": "Move the robot end-effector to a specified object with optional offset. The robot will use inverse kinematics (IK) to reach the target position. Default behavior is to move 10cm above the object.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the target object to move to. Must exist in the scene. Examples: 'cube', 'box', 'Rigidbody_Box'"
                },
                "offset_x": {
                    "type": "number",
                    "description": "X-axis offset in meters from object center. Positive = right, Negative = left. Default: 0.0"
                },
                "offset_y": {
                    "type": "number",
                    "description": "Y-axis offset in meters from object center. Positive = up, Negative = down. Default: 0.1 (10cm above object)"
                },
                "offset_z": {
                    "type": "number",
                    "description": "Z-axis offset in meters from object center. Positive = forward, Negative = backward. Default: 0.0"
                },
                "duration": {
                    "type": "number",
                    "description": "Movement duration in seconds. Longer duration = slower movement. Default: 2.0"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "grasp_object",
        "description": "Grasp object using magnetic attachment. Process: 1) Move to EXACTLY 10cm above object, 2) Magnetically attach object to gripper, 3) Wait 2 seconds to stabilize (prevent weird gravity effects), 4) Lift object. Object must have RigidBody enabled.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the object to grasp. Examples: 'Banana', 'Banana 1', 'cube'"
                },
                "lift_height": {
                    "type": "number",
                    "description": "Height to lift after grasping, in meters. Default: 0.5"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "release_object",
        "description": "Release the currently grasped object. Process: 1) (Optional) Lift gripper before release, 2) Detach object from gripper (SetParent to scene root), 3) Object falls due to gravity. Requires object has RigidBody enabled.",
        "parameters": {
            "type": "object",
            "properties": {
                "lift_before_release": {
                    "type": "boolean",
                    "description": "Whether to lift gripper before releasing. Recommended for clearer drop effect. Default: true"
                },
                "lift_height": {
                    "type": "number",
                    "description": "Height to lift before releasing, in meters. Only applies if lift_before_release is true. Default: 0.1"
                }
            },
            "required": []
        }
    },
    {
        "name": "move_to_position",
        "description": "Move robot end-effector to a specific 3D position. CRITICAL: Y-axis is VERTICAL (up/down), Z-axis is forward/back. Can be absolute (world coordinates) or relative (from current position).",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {
                    "type": "number",
                    "description": "X coordinate (left/right) in meters. Negative=left, Positive=right. In absolute mode: world X. In relative mode: offset from current X."
                },
                "y": {
                    "type": "number",
                    "description": "Y coordinate (UP/DOWN - VERTICAL!) in meters. Negative=down, Positive=up. In absolute mode: world Y. In relative mode: offset from current Y. For 'move up': use positive Y. For 'move down': use negative Y."
                },
                "z": {
                    "type": "number",
                    "description": "Z coordinate (forward/back) in meters. Negative=backward, Positive=forward. In absolute mode: world Z. In relative mode: offset from current Z."
                },
                "duration": {
                    "type": "number",
                    "description": "Movement duration in seconds. Default: 2.0"
                },
                "relative": {
                    "type": "boolean",
                    "description": "If true, (x,y,z) are offsets from current position. If false, they are absolute world coordinates. Default: false"
                }
            },
            "required": ["x", "y", "z"]
        }
    }
]

TOOL_SCHEMAS = [{"type": "function", "function": f} for f in FUNCTION_SCHEMAS]


# ============================================================================
# User Prompt Templates
# ============================================================================

USER_PROMPT_TEMPLATES = {
    "explore_scene": "Show me all objects in the scene",
    "find_object": "Where is the {object_name}?",
    "move_to_object": "Move to the {object_name}",
    "move_above_object": "Move {distance} above the {object_name}",
    "grasp_object": "Grasp the {object_name}",
    "release_object": "Release the object",
    "move_to_position": "Move to position x={x}, y={y}, z={z}",
    "move_relative": "Move {distance} {direction}",
}


# ============================================================================
# Error Messages
# ============================================================================

ERROR_MESSAGES = {
    "object_not_found": "I couldn't find an object named '{name}' in the scene. Would you like me to show you all available objects?",
    "movement_failed": "The robot couldn't complete the movement to {target}. This might be due to: 1) Target out of reach, 2) Joint limits, or 3) Collision. Would you like to try a different approach?",
    "grasp_failed": "I couldn't grasp the {name}. Please check: 1) Object is within reach, 2) Gripper is properly aligned, 3) Object is graspable.",
    "no_object_grasped": "There's no object currently grasped. Please grasp an object first before trying to release it.",
    "api_error": "I encountered an error communicating with the robot: {error}. Please check the Unity connection.",
}


# ============================================================================
# Success Messages
# ============================================================================

SUCCESS_MESSAGES = {
    "info_retrieved": "I found {count} object(s) in the scene.",
    "moved_to_object": "Successfully moved to {name}. The robot is now positioned {offset_description}.",
    "grasped_object": "Successfully grasped {name}! The object is now held by the gripper and lifted {lift_height}m.",
    "released_object": "Successfully released the object.",
    "moved_to_position": "Successfully moved to position ({x}, {y}, {z}).",
}


# ============================================================================
# Helper Functions for Prompt Generation
# ============================================================================

def format_user_prompt(template_key: str, **kwargs) -> str:
    """
    Format a user prompt template with given parameters.

    Args:
        template_key: Key from USER_PROMPT_TEMPLATES
        **kwargs: Variables to substitute in template

    Returns:
        Formatted prompt string

    Example:
        prompt = format_user_prompt("find_object", object_name="cube")
        # Returns: "Where is the cube?"
    """
    if template_key not in USER_PROMPT_TEMPLATES:
        raise ValueError(f"Unknown template key: {template_key}")

    template = USER_PROMPT_TEMPLATES[template_key]
    return template.format(**kwargs)


def get_error_message(error_key: str, **kwargs) -> str:
    """
    Get a formatted error message.

    Args:
        error_key: Key from ERROR_MESSAGES
        **kwargs: Variables to substitute in message

    Returns:
        Formatted error message

    Example:
        msg = get_error_message("object_not_found", name="cube")
    """
    if error_key not in ERROR_MESSAGES:
        return f"An unknown error occurred: {error_key}"

    message = ERROR_MESSAGES[error_key]
    return message.format(**kwargs)


def get_success_message(success_key: str, **kwargs) -> str:
    """
    Get a formatted success message.

    Args:
        success_key: Key from SUCCESS_MESSAGES
        **kwargs: Variables to substitute in message

    Returns:
        Formatted success message

    Example:
        msg = get_success_message("moved_to_object", name="cube", offset_description="10cm above")
    """
    if success_key not in SUCCESS_MESSAGES:
        return f"Operation completed: {success_key}"

    message = SUCCESS_MESSAGES[success_key]
    return message.format(**kwargs)


# ============================================================================
# Prompt Variations for Different Use Cases
# ============================================================================

BRIEF_SYSTEM_PROMPT = """You are a robot control assistant. Help users control a Kinova Gen3 robot using the available functions. Be concise and clear."""

DETAILED_SYSTEM_PROMPT = SYSTEM_PROMPT  # Alias for clarity

BEGINNER_SYSTEM_PROMPT = """You are a friendly robot control assistant designed for beginners.

You help users control a Kinova Gen3 robotic arm. Always:
- Explain what you're about to do before doing it
- Use simple language and avoid technical jargon
- Offer suggestions when users seem unsure
- Confirm actions before executing potentially risky operations
- Provide helpful hints and tips

Available functions: get_info, move_to_object, grasp_object, release_object, move_to_position

Be patient, encouraging, and educational!
"""


# ============================================================================
# Conversation Context Templates
# ============================================================================

CONVERSATION_STARTERS = [
    "Hello! I'm your robot control assistant. I can help you move the Kinova robot, grasp objects, and explore the scene. What would you like to do?",
    "Hi! I'm ready to help you control the robot. You can ask me to show objects, move the robot, or grasp items. What's your first command?",
    "Welcome! I can control the Kinova robot for you. Try commands like 'show me all objects' or 'move to the cube'. How can I help?",
]


# ============================================================================
# Testing and Validation
# ============================================================================

if __name__ == "__main__":
    """Test prompt definitions"""
    print("="*70)
    print("PROMPT DEFINITIONS TEST")
    print("="*70)

    print("\n1. System Prompt (first 200 chars):")
    print(SYSTEM_PROMPT[:200] + "...")

    print(f"\n2. Number of function schemas: {len(FUNCTION_SCHEMAS)}")
    for schema in FUNCTION_SCHEMAS:
        print(f"   - {schema['name']}")

    print(f"\n3. Number of prompt templates: {len(USER_PROMPT_TEMPLATES)}")

    print("\n4. Testing template formatting:")
    test_prompt = format_user_prompt("find_object", object_name="cube")
    print(f"   Result: {test_prompt}")

    print("\n5. Testing error message:")
    test_error = get_error_message("object_not_found", name="cube")
    print(f"   Result: {test_error}")

    print("\n6. Testing success message:")
    test_success = get_success_message("moved_to_object", name="cube", offset_description="10cm above")
    print(f"   Result: {test_success}")

    print("\n" + "="*70)
    print("All prompts loaded successfully!")
    print("="*70)
