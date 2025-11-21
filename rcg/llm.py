import os
import json
import threading
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# Import prompts from prompt.py
from rcg.prompt import (
    SYSTEM_PROMPT,
    TOOL_SCHEMAS,
    get_error_message,
    get_success_message
)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None
    print("[Warning] OpenAI package not installed. Install with: pip install openai")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# Configuration
# ============================================================================
class LLMConfig:
    """Configuration for LLM API."""

    # OpenAI API settings (using custom Qwen3 API endpoint)
    API_KEY = os.getenv("OPENAI_API_KEY", "")

    # NOTE: BASE_URL typically ends with /v1
    BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Use models supportting function calling
    MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Temperature and other params
    TEMPERATURE = 0.7
    MAX_TOKENS = None  # None = no limit

    # Verbose logging
    VERBOSE = True
    SHOW_FUNCTION_CALLS = True

    # OpenAI client instance (v1.0+ API)
    _client = None

    @classmethod
    def get_client(cls):
        """Get or create OpenAI client instance."""
        if not OPENAI_AVAILABLE:
            raise RuntimeError("OpenAI package not available")

        if cls._client is None:
            cls._client = OpenAI(
                api_key=cls.API_KEY,
                base_url=cls.BASE_URL
            )
        return cls._client

    @classmethod
    def set_api_key(cls, api_key: str):
        """Set OpenAI API key."""
        cls.API_KEY = api_key
        cls._client = None  # Reset client to use new key

    @classmethod
    def set_base_url(cls, base_url: str):
        """Set OpenAI base URL."""
        cls.BASE_URL = base_url
        cls._client = None  # Reset client to use new URL

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

# Thread safety - share lock with gradio_ui if available
_unity_lock = None

# Dummy grasp - track grasped object
_grasped_object = None
_grasped_object_id = None


def initialize(env, robot, gripper, unity_lock=None, api_key: Optional[str] = None, base_url: Optional[str] = None):
    """
    Initialize LLM system with environment and API settings.

    Args:
        env: KinovaTestEnv instance
        robot: Robot ControllerAttr instance
        gripper: Gripper ControllerAttr instance
        unity_lock: Optional threading.Lock for Unity communication thread safety
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
    global _global_env, _global_robot, _global_gripper, _unity_lock

    # Set environment references
    _global_env = env
    _global_robot = robot
    _global_gripper = gripper

    # Set thread lock (create new one if not provided)
    _unity_lock = unity_lock if unity_lock is not None else threading.Lock()

    # Ensure IK is enabled for the robot
    try:
        print("[LLM] Ensuring robot IK is enabled...")
        _global_robot.EnabledNativeIK(True)
        _global_env.step()
        print("[LLM] Robot IK enabled")
    except Exception as e:
        print(f"[LLM Warning] Could not enable IK: {e}")

    # Set initial robot pose and rotation (critical for grasping!)
    try:
        print("[LLM] Setting initial robot pose and rotation...")
        # Higher initial position: Y=1.8m (suitable for objects around Y=1.2m)
        _global_robot.IKTargetDoMove(position=[0, 1.8, 0.5], duration=0, speed_based=False)
        _global_robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
        _global_robot.WaitDo()
        _global_env.step(10)
        print("[LLM] Robot pose initialized (position: [0, 1.8, 0.5], rotation: [0, 45, 180])")
    except Exception as e:
        print(f"[LLM Warning] Could not set initial pose: {e}")

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

def register_unity_object(instance_id: int, attr_type=None) -> Dict[str, Any]:
    """
    Register an existing Unity object with Python environment.

    This is useful for objects that already exist in the Unity scene
    but haven't been created via Python's InstanceObject().

    Args:
        instance_id: The Instance ID of the object in Unity (find in Inspector)
        attr_type: Optional attribute type (default: BaseAttr)

    Returns:
        Dictionary with success status and object info
    """
    _check_initialization()

    try:
        if attr_type is None:
            from pyrcareworld.attributes import BaseAttr
            attr_type = BaseAttr

        def _register_object():
            obj = _global_env.GetAttr(instance_id)
            if obj:
                obj_name = obj.data.get("name", f"Object_{instance_id}")
                obj_type = type(obj).__name__
                return obj_name, obj_type
            return None, None

        # Execute with thread safety
        if _unity_lock:
            with _unity_lock:
                obj_name, obj_type = _register_object()
        else:
            obj_name, obj_type = _register_object()

        if obj_name:
            return {
                "success": True,
                "message": f"Registered object '{obj_name}'",
                "data": {
                    "id": instance_id,
                    "name": obj_name,
                    "type": obj_type
                }
            }
        else:
            return {
                "success": False,
                "message": f"Object with ID {instance_id} not found in Unity scene",
                "data": {}
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error registering object: {str(e)}",
            "data": {}
        }


def get_info(name: Optional[str] = None) -> Dict[str, Any]:
    """Get information about objects in the scene.

    This function retrieves all objects tracked by the environment.
    Only objects with BaseAttr components are included.

    Note: Objects in Unity must be registered with the Python environment.
    Use env.GetAttr(instance_id) to register existing Unity objects.
    """
    _check_initialization()

    try:
        all_objects = []
        matched_objects = []

        # All Unity operations must be protected by lock
        def _collect_objects():
            _global_env.step()
            all_objs = []
            matched_objs = []

            for obj_id, obj_attr in _global_env.attrs.items():
                try:
                    if not hasattr(obj_attr, 'data'):
                        continue

                    obj_data = obj_attr.data
                    obj_name = obj_data.get("name", f"Object_{obj_id}")
                    obj_type = type(obj_attr).__name__

                    if "position" not in obj_data:
                        continue

                    obj_info = {
                        "id": obj_id,
                        "name": obj_name,
                        "type": obj_type,
                        "position": obj_data.get("position", [0.0, 0.0, 0.0]),
                        "rotation": obj_data.get("rotation", [0.0, 0.0, 0.0]),
                        "quaternion": obj_data.get("quaternion", [0.0, 0.0, 0.0, 1.0]),
                    }

                    if "scale" in obj_data:
                        obj_info["scale"] = obj_data["scale"]
                    if "velocity" in obj_data:
                        obj_info["velocity"] = obj_data["velocity"]

                    # Always add to all_objs
                    all_objs.append(obj_info)

                    # Add to matched_objs if name matches or no filter
                    if name is None or name.lower() in obj_name.lower():
                        matched_objs.append(obj_info)

                except Exception as e:
                    continue

            return all_objs, matched_objs

        # Execute with thread safety
        if _unity_lock:
            with _unity_lock:
                all_objects, matched_objects = _collect_objects()
        else:
            all_objects, matched_objects = _collect_objects()

        all_names = [obj['name'] for obj in all_objects]
        matched_names = [obj['name'] for obj in matched_objects]

        if name is not None and len(matched_objects) == 0:
            return {
                "success": False,
                "message": f"Object '{name}' not found. Available: {all_names[:10]}",
                "data": {
                    "total_objects": 0,
                    "objects": [],
                    "searched_name": name,
                    "available_objects": all_names
                }
            }

        return {
            "success": True,
            "message": f"Found {len(matched_objects)} object(s)" + (f" matching '{name}'" if name else " in scene"),
            "data": {
                "total_objects": len(matched_objects),
                "objects": matched_objects,
                "searched_name": name if name else None,
                "all_object_names": matched_names
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
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
        def _execute_move():
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
                return None, None, None, None

            obj_position = target_obj.data.get("position", [0.0, 0.0, 0.0])
            target_position = [
                obj_position[0] + offset_x,
                obj_position[1] + offset_y,
                obj_position[2] + offset_z
            ]

            _global_robot.IKTargetDoMove(
                position=target_position,
                duration=duration,
                speed_based=speed_based
            )
            _global_robot.WaitDo()
            _global_env.step(50)

            return target_obj, target_obj_id, obj_position, target_position

        # Execute with thread safety
        if _unity_lock:
            with _unity_lock:
                target_obj, target_obj_id, obj_position, target_position = _execute_move()
        else:
            target_obj, target_obj_id, obj_position, target_position = _execute_move()

        if target_obj is None:
            return {
                "success": False,
                "message": f"Object '{name}' not found in scene",
                "data": {}
            }

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
    """
    Grasp a specified object using magnetic attachment (SetParent).

    Process:
    1. Move gripper to EXACTLY 10cm (0.1m) above object
    2. Attach object to gripper via SetParent (magnetic grasp)
    3. Stay still for 2 seconds (stabilize attachment, prevent weird gravity effects)
    4. Lift object by lift_height

    Args:
        name: Object name to grasp
        approach_height: (IGNORED - always uses 0.1m)
        grasp_offset_y: (IGNORED - always uses 0.1m)
        lift_height: Height to lift after grasping (default 0.5m)

    Returns:
        Dict with success status and grasp details
    """
    global _grasped_object, _grasped_object_id
    _check_initialization()

    try:
        def _execute_grasp():
            global _grasped_object, _grasped_object_id  # CRITICAL: Must declare global in nested function!

            print(f"[DUMMY GRASP] Starting dummy grasp for '{name}'")
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
                print(f"[DUMMY GRASP] Object '{name}' not found!")
                return None, None, None, None, None, None

            obj_position = target_obj.data.get("position", [0.0, 0.0, 0.0])
            print(f"[DUMMY GRASP] Object position: {obj_position}")

            # Step 1: Move STRICTLY to 0.1m (10cm) above object
            approach_position = [obj_position[0], obj_position[1] + 0.1, obj_position[2]]
            print(f"[DUMMY GRASP] Step 1: Moving to 10cm above object at {approach_position}")
            _global_robot.IKTargetDoMove(position=approach_position, duration=2, speed_based=False)
            _global_robot.WaitDo()
            _global_env.step(10)
            print(f"[DUMMY GRASP] Positioned 10cm above object")

            # Step 2: Attach object to gripper (MAGNETIC GRASP!)
            print(f"[DUMMY GRASP] Step 2: Activating magnetic attachment (SetParent)")
            target_obj.SetParent(_global_gripper.id, "")
            _global_env.step(50)
            print(f"[DUMMY GRASP] Object magnetically attached! (parent_id={_global_gripper.id})")

            # Store grasped object (global variable)
            _grasped_object = target_obj
            _grasped_object_id = target_obj_id
            print(f"[DUMMY GRASP] Saved to global: _grasped_object={target_obj.data.get('name')} (id={target_obj_id})")

            # Step 3: CRITICAL - Stay still for 2 seconds (prevent weird gravity effects)
            print(f"[DUMMY GRASP] Step 3: Staying still for 2 seconds (stabilizing attachment)...")
            _global_env.step(100)  # ~2 seconds at 50Hz
            print(f"[DUMMY GRASP] Stabilization complete")

            # Step 4: Lift
            print(f"[DUMMY GRASP] Step 4: Lifting by {lift_height}m...")
            _global_robot.IKTargetDoMove(position=[0, lift_height, 0], duration=2, speed_based=False, relative=True)
            _global_robot.WaitDo()
            _global_env.step(10)
            print(f"[DUMMY GRASP] Lift complete")

            final_position = [approach_position[0], approach_position[1] + lift_height, approach_position[2]]
            print(f"[DUMMY GRASP] Magnetic grasp complete! Object is now attached to gripper")

            return target_obj, target_obj_id, obj_position, approach_position, approach_position, final_position

        # Execute with thread safety
        if _unity_lock:
            with _unity_lock:
                result = _execute_grasp()
        else:
            result = _execute_grasp()

        target_obj, target_obj_id, obj_position, approach_position, grasp_position, final_position = result

        if target_obj is None:
            return {
                "success": False,
                "message": f"Object '{name}' not found in scene",
                "data": {}
            }

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
    """
    Release the currently grasped object.

    Process:
    1. (Optional) Lift gripper by lift_height before release
    2. Detach object from gripper via SetParent(0) - object returns to scene root
    3. Object will fall due to gravity (RigidBody must be enabled on object!)

    Args:
        lift_before_release: Whether to lift before releasing (default True)
        lift_height: Height to lift before release (default 0.1m)

    Returns:
        Dict with success status
    """
    global _grasped_object, _grasped_object_id
    _check_initialization()

    try:
        def _execute_release():
            global _grasped_object, _grasped_object_id  # CRITICAL: Must declare global in nested function!

            print(f"[DUMMY RELEASE] Starting dummy release")
            print(f"[DUMMY RELEASE] Current _grasped_object: {_grasped_object}")

            if _grasped_object is None:
                print(f"[DUMMY RELEASE] No object is currently grasped!")
                return False

            if lift_before_release:
                print(f"[DUMMY RELEASE] Step 1: Lifting by {lift_height}m before release...")
                _global_robot.IKTargetDoMove(position=[0, lift_height, 0], duration=1, speed_based=False, relative=True)
                _global_robot.WaitDo()
                _global_env.step(10)

            # Detach object from gripper (remove parent - SetParent(0) = scene root)
            print(f"[DUMMY RELEASE] Step 2: Detaching object from gripper (SetParent 0)")
            _grasped_object.SetParent(0, "")  # 0 = scene root (no parent)
            _global_env.step(100)  # Wait longer to let physics settle
            print(f"[DUMMY RELEASE] Object detached! Object should now fall due to gravity")

            # Clear global tracking
            _grasped_object = None
            _grasped_object_id = None
            print(f"[DUMMY RELEASE] Cleared global tracking")

            return True

        # Execute with thread safety
        if _unity_lock:
            with _unity_lock:
                success = _execute_release()
        else:
            success = _execute_release()

        if not success:
            return {
                "success": False,
                "message": "No object is currently grasped",
                "data": {}
            }

        return {
            "success": True,
            "message": "Successfully released object (dummy release)",
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
    """
    Move robot to an absolute or relative position.

    Coordinate system: X=left/right, Y=up/down, Z=forward/back
    - relative=False: Move to absolute position [x, y, z]
    - relative=True: Move by offset [x, y, z] from current position
    """
    _check_initialization()

    try:
        target_position = [x, y, z]

        def _execute_move():
            # Match direct control implementation (gradio_ui.py)
            _global_robot.IKTargetDoMove(
                position=target_position,
                duration=duration if not relative else 1.0,  # Use 1.0s for relative moves
                speed_based=False,  # Always use duration-based for consistency
                relative=relative
            )
            _global_robot.WaitDo()
            _global_env.step(50)

        # Execute with thread safety
        if _unity_lock:
            with _unity_lock:
                _execute_move()
        else:
            _execute_move()

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
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None, enable_logging: bool = True):
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

        # Initialize logging
        self.enable_logging = enable_logging
        if self.enable_logging:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_dir = Path(__file__).parent.parent / "log"
            log_dir.mkdir(exist_ok=True)
            self.log_file = log_dir / f"llm_{timestamp}.log"
            self._write_log(f"=== LLM Session Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
            self._write_log(f"Model: {LLMConfig.MODEL}")
            self._write_log(f"Base URL: {LLMConfig.BASE_URL}")
            self._write_log("")

        print(f"[LLM Controller] Initialized with {LLMConfig.MODEL}")
        if self.enable_logging:
            print(f"[LLM Controller] Logging to {self.log_file}")
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """Process user command using OpenAI function calling."""
        # Log user input
        if self.enable_logging:
            self._write_log("─" * 80)
            self._write_log(f"[{datetime.now().strftime('%H:%M:%S')}] USER: {user_input}")
            self._write_log("")

        self.conversation_history.append({"role": "user", "content": user_input})

        try:
            # Call OpenAI API (v1.0+ API)
            client = LLMConfig.get_client()
            response = client.chat.completions.create(
                model=LLMConfig.MODEL,
                messages=self.conversation_history,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                parallel_tool_calls=True,
                temperature=LLMConfig.TEMPERATURE
            )

            message = response.choices[0].message

            # Check for function call
            if hasattr(message, 'tool_calls') and message.tool_calls:
                function_names = []
                function_args_list = []
                function_results = []

                for call in message.tool_calls:
                    function_name = call.function.name
                    function_names.append(function_name)
                    function_args = json.loads(call.function.arguments)
                    function_args_list.append(function_args)

                    # Log function call
                    if self.enable_logging:
                        self._write_log(f"FUNCTION CALL: {function_name}")
                        self._write_log(f"Arguments: {json.dumps(function_args, indent=2, ensure_ascii=False)}")
                        self._write_log("")

                    if LLMConfig.SHOW_FUNCTION_CALLS:
                        print(f"\n[LLM] Calling function: {function_name}")
                        print(f"[LLM] Arguments: {json.dumps(function_args, indent=2)}")

                    # Execute function
                    function_result = execute_function(function_name, function_args)
                    function_results.append(function_result if function_result else {})

                    # Log function result
                    if self.enable_logging:
                        self._write_log(f"FUNCTION RESULT:")
                        self._write_log(f"  Success: {function_result.get('success', False)}")
                        self._write_log(f"  Message: {function_result.get('message', 'N/A')}")
                        if function_result.get('data'):
                            data_str = json.dumps(function_result['data'], indent=2, ensure_ascii=False)
                            self._write_log(f"  Data: {data_str}")
                        self._write_log("")
                    
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
                final_response = client.chat.completions.create(
                    model=LLMConfig.MODEL,
                    messages=self.conversation_history,
                    temperature=LLMConfig.TEMPERATURE
                )

                final_message = final_response.choices[0].message.content
                self.conversation_history.append({"role": "assistant", "content": final_message})

                # Log LLM response
                if self.enable_logging:
                    self._write_log(f"LLM RESPONSE:")
                    self._write_log(final_message)
                    self._write_log("")

                return {
                    "success": True,
                    "function_called": function_names,
                    "function_args": function_args_list,
                    "function_result": function_results,
                    "llm_response": final_message
                }
            else:
                # No function call at all
                self.conversation_history.append({"role": "assistant", "content": message.content})

                # Log LLM response
                if self.enable_logging:
                    self._write_log(f"LLM RESPONSE (no function call):")
                    self._write_log(message.content)
                    self._write_log("")

                return {
                    "success": True,
                    "function_called": None,
                    "llm_response": message.content
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
        if self.enable_logging:
            self._write_log("\n" + "="*80)
            self._write_log("CONVERSATION RESET")
            self._write_log("="*80 + "\n")

    def _write_log(self, message: str):
        """Write message to log file."""
        if not self.enable_logging:
            return
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
        except Exception as e:
            print(f"[Warning] Failed to write log: {e}")

    def _parse_manual_function_call(self, text: str) -> Optional[tuple]:
        """
        Manually parse JSON-formatted function calls from LLM output.
        Returns: (function_name, function_args) or None
        """
        import re

        # Remove <think> tag content
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

        # Find JSON-formatted function calls
        # Pattern matches: {"function": "xxx", "args": {...}}
        json_pattern = r'\{["\']function["\']\s*:\s*["\'](\w+)["\']\s*,\s*["\']args["\']\s*:\s*(\{[^}]*\})\s*\}'

        match = re.search(json_pattern, text)
        if match:
            function_name = match.group(1)
            args_str = match.group(2)
            try:
                function_args = json.loads(args_str)
                return (function_name, function_args)
            except:
                pass

        # Also try matching JSON in code blocks
        code_block_pattern = r'```json\s*\n\s*\{["\']function["\']\s*:\s*["\'](\w+)["\']\s*,\s*["\']args["\']\s*:\s*(\{[^}]*\})\s*\}\s*\n\s*```'
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            function_name = match.group(1)
            args_str = match.group(2)
            try:
                function_args = json.loads(args_str)
                return (function_name, function_args)
            except:
                pass

        return None
