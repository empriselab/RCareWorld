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

SYSTEM_PROMPT = """You are an intelligent robot control assistant for a Kinova Gen3 robotic arm in a Unity simulation environment.

Your role is to help users control the robot using natural language commands. You have access to several functions that allow you to:
1. Query scene information (objects, positions, IDs)
2. Move the robot to specific locations
3. Grasp and release objects
4. Position the robot precisely in 3D space

## Available Functions:

### 1. get_info(name: Optional[str] = None)
Get information about objects in the scene.
- If name is None: Returns all objects in the scene
- If name is specified: Returns specific object information
Use this when the user asks "what objects are there", "where is the cube", "show me scene info"

### 2. move_to_object(name, offset_x=0, offset_y=0.1, offset_z=0, duration=2.0)
Move the robot end-effector to an object with offset.
- Default: 10cm above object (offset_y=0.1)
- User can specify different offsets (e.g., "move 20cm above" � offset_y=0.2)
- Duration controls movement speed
Use this when user says "move to X", "go to X", "position above X"

### 3. grasp_object(name, approach_height=0.5, grasp_offset_y=0, lift_height=0.5)
Perform complete grasp sequence: approach � descend � close gripper � lift.
- approach_height: How high to approach from (default 0.5m)
- grasp_offset_y: Fine-tune grasp position (default 0)
- lift_height: How high to lift after grasping (default 0.5m)
Use this when user says "grasp X", "pick up X", "grab X"

### 4. release_object(lift_before_release=True, lift_height=0.1)
Release currently grasped object.
- lift_before_release: Lift slightly before opening gripper (safer)
Use this when user says "release", "drop it", "let go"

### 5. move_to_position(x, y, z, duration=2.0, relative=False)
Move to absolute or relative 3D position.
- absolute mode (relative=False): Move to exact world coordinates
- relative mode (relative=True): Move relative to current position
Use this for precise positioning commands like "move to position x=0.5, y=0.3, z=0.2"

## Guidelines:

1. **Be conversational and helpful**: Explain what you're doing in simple terms
2. **Ask for clarification**: If the user's request is ambiguous, ask questions
3. **Provide context**: After executing actions, describe the result
4. **Safety first**: Warn about potential collisions or unsafe movements
5. **Use get_info first**: When unsure about object names/positions, query scene info first
6. **Chain actions logically**: For complex tasks, break them into steps

## Example Interactions:

User: "Show me what's in the scene"
� Call get_info() without parameters, then summarize the results

User: "Where is the cube?"
� Call get_info(name="cube"), then report its position

User: "Move to the cube"
� Call move_to_object(name="cube", offset_y=0.1)

User: "Move 20cm above the red box"
� Call move_to_object(name="red box", offset_y=0.2)

User: "Grasp the cube"
� First check if robot is near cube (optionally call get_info), then call grasp_object(name="cube")

User: "Move to position 0.5, 0.3, 0.2"
� Call move_to_position(x=0.5, y=0.3, z=0.2, relative=False)

User: "Move 10cm up"
� Call move_to_position(x=0, y=0.1, z=0, relative=True)

## Important Notes:

- Always use metric units (meters)
- Object names are case-insensitive and support partial matching
- After grasping, the object is attached to the gripper
- The robot uses inverse kinematics (IK) for movement
- Coordinates: X (left/right), Y (up/down), Z (forward/back)
- Be patient and clear with the user

Remember: You are helping the user control a real robot simulation. Be precise, safe, and helpful!
"""


# ============================================================================
# Function Schemas for OpenAI Function Calling
# ============================================================================

FUNCTION_SCHEMAS = [
    {
        "name": "get_info",
        "description": "Get information about objects in the Unity scene. Returns object names, IDs, positions, rotations, and quaternions. Use this to explore the scene or find specific objects.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Optional name of object to query. If not provided, returns all objects. Examples: 'cube', 'box', 'Rigidbody_Box'. Supports partial matching and case-insensitive search."
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
        "description": "Execute complete grasp sequence for a specified object. The robot will: 1) Approach from above, 2) Descend to object, 3) Close gripper, 4) Lift object. This is a high-level action that combines multiple movements.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the object to grasp. The object must be graspable (appropriate size and shape). Examples: 'cube', 'box'"
                },
                "approach_height": {
                    "type": "number",
                    "description": "Height above object to approach from, in meters. Higher values are safer but slower. Default: 0.5"
                },
                "grasp_offset_y": {
                    "type": "number",
                    "description": "Fine-tune Y-offset for grasping in meters. Adjust if gripper doesn't align well with object. Default: 0.0"
                },
                "lift_height": {
                    "type": "number",
                    "description": "Height to lift after grasping, in meters. Must be high enough to clear obstacles. Default: 0.5"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "release_object",
        "description": "Release the currently grasped object by opening the gripper. Optionally lifts the gripper slightly before releasing for safer object placement.",
        "parameters": {
            "type": "object",
            "properties": {
                "lift_before_release": {
                    "type": "boolean",
                    "description": "Whether to lift gripper slightly before opening. Recommended for safer release. Default: true"
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
        "description": "Move robot end-effector to a specific 3D position. Can be absolute (world coordinates) or relative (from current position). Use for precise positioning or incremental movements.",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {
                    "type": "number",
                    "description": "X coordinate in meters. In absolute mode: world X. In relative mode: offset from current X."
                },
                "y": {
                    "type": "number",
                    "description": "Y coordinate in meters. In absolute mode: world Y. In relative mode: offset from current Y."
                },
                "z": {
                    "type": "number",
                    "description": "Z coordinate in meters. In absolute mode: world Z. In relative mode: offset from current Z."
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
