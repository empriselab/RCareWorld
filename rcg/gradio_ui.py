import gradio as gr
import numpy as np
import time
import threading
from typing import Optional, Tuple, List
import io
from PIL import Image

# Global references (will be set by initialize())
_global_env = None
_global_robot = None
_global_gripper = None
_global_camera = None
_global_llm_controller = None

# Camera feed state
_camera_running = False
_latest_frame = None

# Thread safety - prevent camera and control operations from conflicting
_unity_lock = threading.Lock()

# Control settings
MOVEMENT_DISTANCE = 0.25  # Movement distance in meters (25cm)


def get_unity_lock():
    """Get the Unity communication lock for thread safety."""
    return _unity_lock


# ============================================================================
# Initialization
# ============================================================================

def initialize(env, robot, gripper, camera, llm_controller):
    """
    Initialize the Gradio UI with environment references.

    Args:
        env: KinovaTestEnv instance
        robot: Robot controller attribute
        gripper: Gripper attribute
        camera: Camera attribute
        llm_controller: LLM controller instance
    """
    global _global_env, _global_robot, _global_gripper, _global_camera, _global_llm_controller
    _global_env = env
    _global_robot = robot
    _global_gripper = gripper
    _global_camera = camera
    _global_llm_controller = llm_controller

    print("[Gradio UI] Initialized with environment references")


# ============================================================================
# Camera Feed Functions
# ============================================================================

def start_camera_feed():
    """Start the camera feed update loop."""
    global _camera_running
    _camera_running = True

    def camera_loop():
        global _latest_frame
        while _camera_running:
            try:
                # Use lock to prevent conflicts with control operations
                with _unity_lock:
                    # Capture image from camera
                    _global_camera.GetRGB(width=640, height=480)
                    _global_env.step(1)  # Single step to update

                    # Get image bytes
                    image_bytes = _global_camera.data.get("rgb")
                    if image_bytes:
                        # Convert bytes to PIL Image
                        image = Image.open(io.BytesIO(image_bytes))
                        _latest_frame = np.array(image)

                # ~10 FPS = ~0.1 second delay
                # time.sleep(0.01)

            except Exception as e:
                print(f"[Camera Feed Error] {e}")
                time.sleep(0.5)  # Longer delay on error

    # Start camera thread
    camera_thread = threading.Thread(target=camera_loop, daemon=True)
    camera_thread.start()
    print("[Camera Feed] Started (~10 FPS)")


def stop_camera_feed():
    """Stop the camera feed."""
    global _camera_running
    _camera_running = False
    print("[Camera Feed] Stopped")


def get_latest_frame():
    """Get the latest camera frame."""
    if _latest_frame is not None:
        return _latest_frame
    else:
        # Return placeholder image
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
        placeholder[:, :] = [50, 50, 50]  # Dark gray
        return placeholder


# ============================================================================
# Movement Control Button Functions
# ============================================================================

def move_up() -> str:
    """Move robot up by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_robot.IKTargetDoMove(
                position=[0, MOVEMENT_DISTANCE, 0],
                duration=1.0,
                speed_based=False,
                relative=True
            )
            _global_robot.WaitDo()
            _global_env.step(50)  # Let the environment update
        return f"✓ Moved up {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def move_down() -> str:
    """Move robot down by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_robot.IKTargetDoMove(
                position=[0, -MOVEMENT_DISTANCE, 0],
                duration=1.0,
                speed_based=False,
                relative=True
            )
            _global_robot.WaitDo()
            _global_env.step(50)  # Let the environment update
        return f"✓ Moved down {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def move_left() -> str:
    """Move robot left by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_robot.IKTargetDoMove(
                position=[MOVEMENT_DISTANCE, 0, 0],
                duration=1.0,
                speed_based=False,
                relative=True
            )
            _global_robot.WaitDo()
            _global_env.step(50)  # Let the environment update
        return f"✓ Moved left {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def move_right() -> str:
    """Move robot right by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_robot.IKTargetDoMove(
                position=[-MOVEMENT_DISTANCE, 0, 0],
                duration=1.0,
                speed_based=False,
                relative=True
            )
            _global_robot.WaitDo()
            _global_env.step(50)  # Let the environment update
        return f"✓ Moved right {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def grasp_action() -> str:
    """Close the gripper."""
    try:
        with _unity_lock:  # Thread safety
            _global_gripper.GripperClose()
            _global_env.step(50)
        return "✓ Gripper closed"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def release_action() -> str:
    """Open the gripper."""
    try:
        with _unity_lock:  # Thread safety
            _global_gripper.GripperOpen()
            _global_env.step(50)
        return "✓ Gripper opened"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"

# ============================================================================
# Camera Control Button Functions
# ============================================================================

def move_camera_up() -> str:
    """Move camera up by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_camera.DoMove(
                position=[0, MOVEMENT_DISTANCE, 0],
                duration=1.0,
                speed_based=False,
                relative=True
            )
        return f"✓ Moved camera up {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def move_camera_down() -> str:
    """Move camera down by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_camera.DoMove(
                position=[0, -MOVEMENT_DISTANCE, 0],
                duration=1.0,
                speed_based=False,
                relative=True
            )
        return f"✓ Moved camera down {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def move_camera_left() -> str:
    """Move camera left by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_camera.DoMove(
                position=[MOVEMENT_DISTANCE, 0, 0],
                duration=1.0,
                speed_based=False,
                relative=True
            )
        return f"✓ Moved camera left {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def move_camera_right() -> str:
    """Move camera right by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_camera.DoMove(
                position=[-MOVEMENT_DISTANCE, 0, 0],
                duration=1.0,
                speed_based=False,
                relative=True
            )
        return f"✓ Moved camera right {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"

def move_camera_forward() -> str:
    """Move camera forward by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_camera.DoMove(
                position=[0, 0, -MOVEMENT_DISTANCE],
                duration=1.0,
                speed_based=False,
                relative=True
            )
        return f"✓ Moved camera forward {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


def move_camera_back() -> str:
    """Move camera back by configured distance."""
    try:
        with _unity_lock:  # Thread safety
            _global_camera.DoMove(
                position=[0, 0, MOVEMENT_DISTANCE],
                duration=1.0,
                speed_based=False,
                relative=True
            )
        return f"✓ Moved camera back {int(MOVEMENT_DISTANCE*100)}cm"
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"✗ Error: {str(e)}"


# ============================================================================
# Chat Interface Functions
# ============================================================================

def process_chat_message(message: str, history: List[dict]) -> Tuple[List[dict], str]:
    """
    Process user message through LLM controller.

    Args:
        message: User input message
        history: Chat history (list of message dicts with 'role' and 'content')

    Returns:
        Tuple of (updated_history, status_message)
    """
    if not message.strip():
        return history, "Please enter a message"

    try:
        # Process command with LLM
        result = _global_llm_controller.process_command(message)

        # Build response message
        if result["success"]:
            response_parts = []

            # Add function call info if available
            if result.get("function_called"):
                func_result = result.get("function_result", {})
                func_name = result["function_called"]

                if func_result.get("success"):
                    response_parts.append(f"**[Function: {func_name}]** ✓ {func_result.get('message', 'Done')}")
                else:
                    response_parts.append(f"**[Function: {func_name}]** ✗ {func_result.get('message', 'Failed')}")

            # Add LLM response
            response_parts.append(result["llm_response"])

            bot_response = "\n\n".join(response_parts)
            status = "✓ Command processed successfully"
        else:
            bot_response = f"Error: {result.get('error', 'Unknown error')}"
            status = "✗ Command failed"

        # Update history with messages format
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": bot_response})

        return history, status

    except Exception as e:
        error_msg = f"Error processing command: {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return history, f"✗ {error_msg}"


# ============================================================================
# Gradio Interface Builder
# ============================================================================

def create_interface() -> gr.Blocks:
    """
    Create the Gradio interface with the specified layout.

    Layout:
        - Top: Camera feed (real-time streaming)
        - Bottom:
            - Left: Control buttons (Up/Down/Left/Right/Grasp/Release)
            - Right: Chat interface (input + output)

    Returns:
        Gradio Blocks interface
    """

    with gr.Blocks(
        title="RCareGen",
        theme=gr.themes.Soft(),
        css="""
        * {
            font-family: 'Georgia', 'Palatino Linotype', 'Book Antiqua', 'Times New Roman', serif !important;
            font-style: italic;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Georgia', 'Palatino Linotype', 'Book Antiqua', 'Times New Roman', serif !important;
            font-style: italic;
        }
        /* Fixed width for direction buttons and fill container */
        .direction-btn button {
            width: 100% !important;
            min-width: 100px !important;
        }
        /* Make movement control rows fill full width */
        .movement-controls-grid {
            width: 100% !important;
        }
        .movement-controls-grid > .row {
            width: 100% !important;
        }
        """
    ) as interface:

        # Title
        gr.Markdown("# RCareGen")

        # Top: Camera Feed and controls
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown(f"**Camera Controls** ({int(MOVEMENT_DISTANCE*100)}cm increments)")

                    # 3x3 Grid for directional controls with equal-width columns
                    # Row 1: Empty, Up, Empty
                    with gr.Row():
                            gr.HTML("<div></div>")  # Empty spacer
                            camera_up = gr.Button("⬆️ Up", variant="primary", elem_classes=["direction-btn"])
                            gr.HTML("<div></div>")  # Empty spacer

                    # Row 2: Left, Empty, Right
                    with gr.Row():
                            camera_left = gr.Button("⬅️ Left", variant="primary", elem_classes=["direction-btn"])
                            gr.HTML("")  # Empty spacer
                            camera_right = gr.Button("➡️ Right", variant="primary", elem_classes=["direction-btn"])

                    # Row 3: Empty, Down, Empty
                    with gr.Row():
                            gr.HTML("")  # Empty spacer
                            camera_down = gr.Button("⬇️ Down", variant="primary", elem_classes=["direction-btn"])
                            gr.HTML("")  # Empty spacer

                    # Row 4: Forward, Back
                    with gr.Row():
                            camera_forward = gr.Button("Forward", variant="primary", elem_classes=["direction-btn"])
                            camera_back = gr.Button("Back", variant="primary", elem_classes=["direction-btn"])
            
            # Right Panel: Camera Feed    
            with gr.Column(scale=2):
                camera_feed = gr.Image(
                    label="Robot Camera Feed (~10 FPS)",
                    type="numpy"
                )

        # Timer for periodic camera updates (Gradio 4.0 style)
        timer = gr.Timer(value=0.1, active=True)

        # Bottom: Control Panels
        with gr.Row():

            # Left Panel: Control Buttons
            with gr.Column(scale=1):
                gr.Markdown("### Direct Control")

                with gr.Group():
                    gr.Markdown(f"**Movement Controls** ({int(MOVEMENT_DISTANCE*100)}cm increments)")

                    # 3x3 Grid for directional controls with equal-width columns
                    # Row 1: Empty, Up, Empty
                    with gr.Row():
                            gr.HTML("")  # Empty spacer
                            btn_up = gr.Button("⬆️ Up", variant="primary", elem_classes=["direction-btn"])
                            gr.HTML("")  # Empty spacer

                    # Row 2: Left, Empty, Right
                    with gr.Row():
                            btn_left = gr.Button("⬅️ Left", variant="primary", elem_classes=["direction-btn"])
                            gr.HTML("")  # Empty spacer
                            btn_right = gr.Button("➡️ Right", variant="primary", elem_classes=["direction-btn"])

                    # Row 3: Empty, Down, Empty
                    with gr.Row():
                            gr.HTML("")  # Empty spacer
                            btn_down = gr.Button("⬇️ Down", variant="primary", elem_classes=["direction-btn"])
                            gr.HTML("")  # Empty spacer

                with gr.Group():
                    gr.Markdown("**Gripper Controls**")
                    btn_grasp = gr.Button("Grasp (Close)", variant="secondary")
                    btn_release = gr.Button("Release (Open)", variant="secondary")

                # Status display for button actions
                btn_status = gr.Textbox(
                    label="Action Status",
                    value="Ready",
                    interactive=False,
                    lines=2
                )

            # Right Panel: Chat Interface
            with gr.Column(scale=2):
                gr.Markdown("### Natural Language Control")

                # Chat history
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=400,
                    show_label=True,
                    type='messages'  # Use new messages format for Gradio 5.x
                )

                # User input
                with gr.Row():
                    chat_input = gr.Textbox(
                        label="Your Command",
                        placeholder="Type your command here (e.g., 'move to the cube', 'grasp the box')...",
                        scale=4,
                        lines=1
                    )
                    chat_submit = gr.Button("Send", variant="primary", scale=1)

                # Chat status
                chat_status = gr.Textbox(
                    label="Status",
                    value="Ready",
                    interactive=False,
                    lines=1
                )

                # Example commands
                gr.Markdown("""
                **Example Commands:**
                - *Show me all objects in the scene*
                - *Move to the cube*
                - *Move 20cm above the red box*
                - *Grasp the object*
                - *Release the object*
                """)

        # ========================================================================
        # Event Handlers
        # ========================================================================

        # Camera feed update (Gradio 4.0 Timer-based update)
        timer.tick(
            fn=get_latest_frame,
            inputs=None,
            outputs=camera_feed
        )

        # Camera movement button handlers
        camera_up.click(fn=move_camera_up, inputs=None, outputs=btn_status)
        camera_down.click(fn=move_camera_down, inputs=None, outputs=btn_status)
        camera_left.click(fn=move_camera_left, inputs=None, outputs=btn_status)
        camera_right.click(fn=move_camera_right, inputs=None, outputs=btn_status)
        camera_forward.click(fn=move_camera_forward, inputs=None, outputs=btn_status)
        camera_back.click(fn=move_camera_back, inputs=None, outputs=btn_status)

        # Movement button handlers
        btn_up.click(fn=move_up, inputs=None, outputs=btn_status)
        btn_down.click(fn=move_down, inputs=None, outputs=btn_status)
        btn_left.click(fn=move_left, inputs=None, outputs=btn_status)
        btn_right.click(fn=move_right, inputs=None, outputs=btn_status)

        # Gripper button handlers
        btn_grasp.click(fn=grasp_action, inputs=None, outputs=btn_status)
        btn_release.click(fn=release_action, inputs=None, outputs=btn_status)

        # Chat interface handlers
        chat_submit.click(
            fn=process_chat_message,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_status]
        ).then(
            lambda: "",  # Clear input after sending
            inputs=None,
            outputs=chat_input
        )

        # Allow Enter key to submit
        chat_input.submit(
            fn=process_chat_message,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_status]
        ).then(
            lambda: "",  # Clear input after sending
            inputs=None,
            outputs=chat_input
        )

    return interface


# ============================================================================
# Launch Function
# ============================================================================

def launch_interface(share: bool = False, server_port: int = 7860):
    """
    Launch the Gradio interface.

    Args:
        share: If True, create a public link
        server_port: Port to run the server on (default: 7860)
    """
    if _global_env is None:
        raise RuntimeError("Gradio UI not initialized. Call initialize() first.")

    # Start camera feed
    start_camera_feed()

    # Create and launch interface
    interface = create_interface()

    print("\n" + "="*70)
    print("LAUNCHING GRADIO INTERFACE")
    print("="*70)
    print(f"Server will start on http://localhost:{server_port}")
    if share:
        print("Public link will be generated...")
    print("="*70 + "\n")

    interface.launch(
        share=share,
        server_port=server_port,
        server_name="0.0.0.0",  # Allow external connections
        show_error=True
    )


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("This module should not be run directly.")
    print("Import and use launch_interface() from main.py")
