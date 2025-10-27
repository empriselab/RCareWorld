"""
LLM Controller for Kinova Robot
================================

This module handles all LLM-related functionality including:
    - OpenAI API configuration and calls
    - Function execution (get_info, move_to_object, grasp_object, etc.)
    - Conversation management
    - Integration with prompt.py for all prompts

Key Features:
    - Configurable API key and base URL
    - Complete OpenAI function calling implementation
    - Robot control functions
    - Error handling and retries
"""

import os
import json
from typing import Optional, Dict, Any

# Import prompts from prompt.py
from rcg.prompt import (
    SYSTEM_PROMPT,
    FUNCTION_SCHEMAS,
    get_error_message,
    get_success_message
)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[Warning] OpenAI package not installed. Install with: pip install openai")


# ============================================================================
# Configuration
# ============================================================================
class LLMConfig:
    """Configuration for LLM API."""
    
    # OpenAI API settings
    API_KEY = os.getenv("OPENAI_API_KEY", None)
    BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Temperature and other params
    TEMPERATURE = 0.7
    MAX_TOKENS = None  # None = no limit
    
    # Verbose logging
    VERBOSE = True
    SHOW_FUNCTION_CALLS = True
    
    @classmethod
    def set_api_key(cls, api_key: str):
        """Set OpenAI API key."""
        cls.API_KEY = api_key
        if OPENAI_AVAILABLE:
            openai.api_key = api_key
    
    @classmethod
    def set_base_url(cls, base_url: str):
        """Set OpenAI base URL."""
        cls.BASE_URL = base_url
        if OPENAI_AVAILABLE:
            openai.api_base = base_url
    
    @classmethod
    def set_model(cls, model: str):
        """Set OpenAI model."""
        cls.MODEL = model


# ============================================================================
# Global Environment Reference
# ============================================================================
_global_env = None
_global_robot = None
_global_gripper = None


def initialize(env, robot, gripper, api_key: Optional[str] = None, base_url: Optional[str] = None):
    """
    Initialize LLM system with environment and API settings.
    
    Args:
        env: KinovaTestEnv instance
        robot: Robot ControllerAttr instance
        gripper: Gripper ControllerAttr instance
        api_key: Optional OpenAI API key (uses env variable if not provided)
        base_url: Optional OpenAI base URL (uses default if not provided)
    
    Example:
        from rcg.env import KinovaTestEnv
        from rcg import llm
        
        env = KinovaTestEnv()
        robot = env.get_kinova()
        gripper = env.get_gripper()
        llm.initialize(env, robot, gripper, api_key="sk-...")
    """
    global _global_env, _global_robot, _global_gripper
    
    # Set environment references
    _global_env = env
    _global_robot = robot
    _global_gripper = gripper
    
    # Configure API
    if api_key:
        LLMConfig.set_api_key(api_key)
    elif LLMConfig.API_KEY:
        LLMConfig.set_api_key(LLMConfig.API_KEY)
    
    if base_url:
        LLMConfig.set_base_url(base_url)
    
    print(f"[LLM] Initialized")
    print(f"[LLM] Model: {LLMConfig.MODEL}")
    print(f"[LLM] Base URL: {LLMConfig.BASE_URL}")
    print(f"[LLM] API Key: {'Set' if LLMConfig.API_KEY else 'Not set'}")


def _check_initialization():
    """Check if LLM system is properly initialized."""
    if _global_env is None or _global_robot is None or _global_gripper is None:
        raise RuntimeError(
            "LLM not initialized. Call llm.initialize(env, robot, gripper) first."
        )


# ============================================================================
# Robot Control Functions
# ============================================================================

def get_info(name: Optional[str] = None) -> Dict[str, Any]:
    """Get information about objects in the scene."""
    _check_initialization()
    
    try:
        _global_env.step()
        all_objects = []
        
        for obj_id, obj_attr in _global_env.attrs.items():
            obj_data = obj_attr.data
            obj_info = {
                "id": obj_id,
                "name": obj_data.get("name", f"Object_{obj_id}"),
                "position": obj_data.get("position", [0.0, 0.0, 0.0]),
                "rotation": obj_data.get("rotation", [0.0, 0.0, 0.0]),
                "quaternion": obj_data.get("quaternion", [0.0, 0.0, 0.0, 1.0]),
            }
            
            if name is not None:
                if name.lower() in obj_info["name"].lower():
                    all_objects.append(obj_info)
            else:
                all_objects.append(obj_info)
        
        if name is not None and len(all_objects) == 0:
            return {
                "success": False,
                "message": f"Object with name '{name}' not found in scene",
                "data": {"total_objects": 0, "objects": []}
            }
        
        return {
            "success": True,
            "message": f"Found {len(all_objects)} object(s)" + (f" matching '{name}'" if name else ""),
            "data": {"total_objects": len(all_objects), "objects": all_objects}
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting scene info: {str(e)}",
            "data": {"total_objects": 0, "objects": []}
        }


def move_to_object(
    name: str,
    offset_x: float = 0.0,
    offset_y: float = 0.1,
    offset_z: float = 0.0,
    duration: float = 2.0,
    speed_based: bool = False
) -> Dict[str, Any]:
    """Move robot end-effector to a specified object with offset."""
    _check_initialization()
    
    try:
        _global_env.step()
        target_obj = None
        target_obj_id = None
        
        for obj_id, obj_attr in _global_env.attrs.items():
            obj_name = obj_attr.data.get("name", "")
            if name.lower() in obj_name.lower():
                target_obj = obj_attr
                target_obj_id = obj_id
                break
        
        if target_obj is None:
            return {
                "success": False,
                "message": f"Object '{name}' not found in scene",
                "data": {}
            }
        
        obj_position = target_obj.data.get("position", [0.0, 0.0, 0.0])
        target_position = [
            obj_position[0] + offset_x,
            obj_position[1] + offset_y,
            obj_position[2] + offset_z
        ]
        
        print(f"[Move] Object '{name}' (ID: {target_obj_id}) at {obj_position}")
        print(f"[Move] Moving to target position: {target_position}")
        
        _global_robot.IKTargetDoMove(
            position=target_position,
            duration=duration,
            speed_based=speed_based
        )
        _global_robot.WaitDo()
        
        print(f"[Move] Movement completed")
        
        return {
            "success": True,
            "message": f"Successfully moved to object '{name}' with offset",
            "data": {
                "object_name": target_obj.data.get("name", name),
                "object_id": target_obj_id,
                "object_position": obj_position,
                "target_position": target_position,
                "offset_applied": [offset_x, offset_y, offset_z]
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error moving to object: {str(e)}",
            "data": {}
        }


def grasp_object(
    name: str,
    approach_height: float = 0.5,
    grasp_offset_y: float = 0.0,
    lift_height: float = 0.5
) -> Dict[str, Any]:
    """Grasp a specified object using the gripper."""
    _check_initialization()
    
    try:
        _global_env.step()
        target_obj = None
        target_obj_id = None
        
        for obj_id, obj_attr in _global_env.attrs.items():
            obj_name = obj_attr.data.get("name", "")
            if name.lower() in obj_name.lower():
                target_obj = obj_attr
                target_obj_id = obj_id
                break
        
        if target_obj is None:
            return {
                "success": False,
                "message": f"Object '{name}' not found in scene",
                "data": {}
            }
        
        obj_position = target_obj.data.get("position", [0.0, 0.0, 0.0])
        
        print(f"[Grasp] Starting grasp sequence for '{name}' (ID: {target_obj_id})")
        
        # Step 1: Approach
        approach_position = [obj_position[0], obj_position[1] + approach_height, obj_position[2]]
        print(f"[Grasp] Step 1: Moving to approach position {approach_position}")
        _global_robot.IKTargetDoMove(position=approach_position, duration=2, speed_based=False)
        _global_robot.WaitDo()
        
        # Step 2: Descend
        grasp_position = [obj_position[0], obj_position[1] + grasp_offset_y, obj_position[2]]
        print(f"[Grasp] Step 2: Moving down to grasp position {grasp_position}")
        _global_robot.IKTargetDoMove(position=grasp_position, duration=2, speed_based=False)
        _global_robot.WaitDo()
        
        # Step 3: Close gripper
        print(f"[Grasp] Step 3: Closing gripper")
        _global_gripper.GripperClose()
        _global_env.step(50)
        
        # Step 4: Lift
        print(f"[Grasp] Step 4: Lifting object by {lift_height}m")
        _global_robot.IKTargetDoMove(position=[0, lift_height, 0], duration=2, speed_based=False, relative=True)
        _global_robot.WaitDo()
        
        final_position = [grasp_position[0], grasp_position[1] + lift_height, grasp_position[2]]
        
        print(f"[Grasp] Grasp sequence completed")
        
        return {
            "success": True,
            "message": f"Successfully grasped object '{name}' and lifted",
            "data": {
                "object_name": target_obj.data.get("name", name),
                "object_id": target_obj_id,
                "object_position": obj_position,
                "approach_position": approach_position,
                "grasp_position": grasp_position,
                "final_position": final_position
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error grasping object: {str(e)}",
            "data": {}
        }


def release_object(lift_before_release: bool = True, lift_height: float = 0.1) -> Dict[str, Any]:
    """Release the currently grasped object."""
    _check_initialization()
    
    try:
        print(f"[Release] Releasing object")
        
        if lift_before_release:
            print(f"[Release] Lifting {lift_height}m before release")
            _global_robot.IKTargetDoMove(position=[0, lift_height, 0], duration=1, speed_based=False, relative=True)
            _global_robot.WaitDo()
        
        print(f"[Release] Opening gripper")
        _global_gripper.GripperOpen()
        _global_env.step(50)
        
        print(f"[Release] Object released")
        
        return {
            "success": True,
            "message": "Successfully released object",
            "data": {"lift_before_release": lift_before_release, "lift_height": lift_height}
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error releasing object: {str(e)}",
            "data": {}
        }


def move_to_position(
    x: float,
    y: float,
    z: float,
    duration: float = 2.0,
    speed_based: bool = False,
    relative: bool = False
) -> Dict[str, Any]:
    """Move robot to an absolute or relative position."""
    _check_initialization()
    
    try:
        target_position = [x, y, z]
        
        print(f"[Move] Moving to {'relative' if relative else 'absolute'} position: {target_position}")
        
        _global_robot.IKTargetDoMove(
            position=target_position,
            duration=duration,
            speed_based=speed_based,
            relative=relative
        )
        _global_robot.WaitDo()
        
        print(f"[Move] Movement completed")
        
        return {
            "success": True,
            "message": f"Successfully moved to position {target_position}",
            "data": {"target_position": target_position, "relative": relative}
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error moving to position: {str(e)}",
            "data": {}
        }


# ============================================================================
# Function Dispatcher
# ============================================================================

FUNCTION_MAP = {
    "get_info": get_info,
    "move_to_object": move_to_object,
    "grasp_object": grasp_object,
    "release_object": release_object,
    "move_to_position": move_to_position
}


def execute_function(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a function by name with given arguments."""
    if function_name not in FUNCTION_MAP:
        return {
            "success": False,
            "message": f"Unknown function: {function_name}",
            "data": {}
        }
    
    try:
        result = FUNCTION_MAP[function_name](**arguments)
        return result
    except Exception as e:
        return {
            "success": False,
            "message": f"Error executing {function_name}: {str(e)}",
            "data": {}
        }


# ============================================================================
# LLM Controller (OpenAI Integration)
# ============================================================================

class LLMController:
    """LLM controller for processing natural language commands."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """Initialize LLM controller."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed")
        
        # Set API configuration
        if api_key:
            LLMConfig.set_api_key(api_key)
        if base_url:
            LLMConfig.set_base_url(base_url)
        if model:
            LLMConfig.MODEL = model
        
        if not LLMConfig.API_KEY:
            raise ValueError("OpenAI API key not set")
        
        # Initialize conversation history
        self.conversation_history = [{
            "role": "system",
            "content": SYSTEM_PROMPT
        }]
        
        print(f"[LLM Controller] Initialized with {LLMConfig.MODEL}")
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process user command using OpenAI function calling."""
        self.conversation_history.append({"role": "user", "content": user_input})
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=LLMConfig.MODEL,
                messages=self.conversation_history,
                functions=FUNCTION_SCHEMAS,
                function_call="auto",
                temperature=LLMConfig.TEMPERATURE
            )
            
            message = response["choices"][0]["message"]
            
            # Check for function call
            if message.get("function_call"):
                function_name = message["function_call"]["name"]
                function_args = json.loads(message["function_call"]["arguments"])
                
                if LLMConfig.SHOW_FUNCTION_CALLS:
                    print(f"\n[LLM] Calling function: {function_name}")
                    print(f"[LLM] Arguments: {json.dumps(function_args, indent=2)}")
                
                # Execute function
                function_result = execute_function(function_name, function_args)
                
                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {"name": function_name, "arguments": json.dumps(function_args)}
                })
                
                self.conversation_history.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
                
                # Get final response
                final_response = openai.ChatCompletion.create(
                    model=LLMConfig.MODEL,
                    messages=self.conversation_history,
                    temperature=LLMConfig.TEMPERATURE
                )
                
                final_message = final_response["choices"][0]["message"]["content"]
                self.conversation_history.append({"role": "assistant", "content": final_message})
                
                return {
                    "success": True,
                    "function_called": function_name,
                    "function_args": function_args,
                    "function_result": function_result,
                    "llm_response": final_message
                }
            else:
                # No function call
                assistant_message = message["content"]
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                return {
                    "success": True,
                    "function_called": None,
                    "llm_response": assistant_message
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"LLM error: {str(e)}"
            }
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = [self.conversation_history[0]]
        print("[LLM Controller] Conversation history reset")
