"""
Gradio UI for LLM-Controlled Kinova Robot
==========================================

This module provides a web-based interface using Gradio for controlling
the Kinova Gen3 robot with both direct button controls and natural language.

Layout:
    - Top: Real-time camera feed (~10 FPS)
    - Bottom Left: Direct control buttons (Move Up/Down/Left/Right, Grasp, Release)
    - Bottom Right: Chat interface for natural language commands
"""

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
                time.sleep(0.1)

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
# Control Button Functions
# ============================================================================

def move_up() -> str:
    """Move robot up by 10cm."""
    try:
        _global_robot.IKTargetDoMove(
            position=[0, 0.1, 0],  # 10cm up
            duration=1.0,
            speed_based=False,
            relative=True
        )
        _global_robot.WaitDo()
        return "✓ Moved up 10cm"
    except Exception as e:
        return f"✗ Error: {str(e)}"


def move_down() -> str:
    """Move robot down by 10cm."""
    try:
        _global_robot.IKTargetDoMove(
            position=[0, -0.1, 0],  # 10cm down
            duration=1.0,
            speed_based=False,
            relative=True
        )
        _global_robot.WaitDo()
        return "✓ Moved down 10cm"
    except Exception as e:
        return f"✗ Error: {str(e)}"


def move_left() -> str:
    """Move robot left by 10cm."""
    try:
        _global_robot.IKTargetDoMove(
            position=[-0.1, 0, 0],  # 10cm left
            duration=1.0,
            speed_based=False,
            relative=True
        )
        _global_robot.WaitDo()
        return "✓ Moved left 10cm"
    except Exception as e:
        return f"✗ Error: {str(e)}"


def move_right() -> str:
    """Move robot right by 10cm."""
    try:
        _global_robot.IKTargetDoMove(
            position=[0.1, 0, 0],  # 10cm right
            duration=1.0,
            speed_based=False,
            relative=True
        )
        _global_robot.WaitDo()
        return "✓ Moved right 10cm"
    except Exception as e:
        return f"✗ Error: {str(e)}"


def grasp_action() -> str:
    """Close the gripper."""
    try:
        _global_gripper.GripperClose()
        _global_env.step(50)
        return "✓ Gripper closed"
    except Exception as e:
        return f"✗ Error: {str(e)}"


def release_action() -> str:
    """Open the gripper."""
    try:
        _global_gripper.GripperOpen()
        _global_env.step(50)
        return "✓ Gripper opened"
    except Exception as e:
        return f"✗ Error: {str(e)}"


# ============================================================================
# Chat Interface Functions
# ============================================================================

def process_chat_message(message: str, history: List[List[str]]) -> Tuple[List[List[str]], str]:
    """
    Process user message through LLM controller.

    Args:
        message: User input message
        history: Chat history (list of [user_msg, bot_msg] pairs)

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

        # Update history
        history.append([message, bot_response])

        return history, status

    except Exception as e:
        error_msg = f"Error processing command: {str(e)}"
        history.append([message, error_msg])
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

    with gr.Blocks(title="Kinova Robot Control", theme=gr.themes.Soft()) as interface:

        # Title
        gr.Markdown("# 🤖 Kinova Robot Control Interface")
        gr.Markdown("Control the robot using direct buttons or natural language commands")

        # Top: Camera Feed
        with gr.Row():
            camera_feed = gr.Image(
                label="Robot Camera Feed (~10 FPS)",
                type="numpy",
                streaming=True,
                every=0.1  # Update every 100ms (~10 FPS)
            )

        # Bottom: Control Panels
        with gr.Row():

            # Left Panel: Control Buttons
            with gr.Column(scale=1):
                gr.Markdown("### 🎮 Direct Control")

                with gr.Group():
                    gr.Markdown("**Movement Controls** (10cm increments)")

                    # Up button
                    with gr.Row():
                        gr.Column(scale=1)  # Spacer
                        btn_up = gr.Button("⬆️ Up", variant="primary", scale=2)
                        gr.Column(scale=1)  # Spacer

                    # Left/Right buttons
                    with gr.Row():
                        btn_left = gr.Button("⬅️ Left", variant="primary", scale=1)
                        gr.Column(scale=1)  # Spacer
                        btn_right = gr.Button("➡️ Right", variant="primary", scale=1)

                    # Down button
                    with gr.Row():
                        gr.Column(scale=1)  # Spacer
                        btn_down = gr.Button("⬇️ Down", variant="primary", scale=2)
                        gr.Column(scale=1)  # Spacer

                with gr.Group():
                    gr.Markdown("**Gripper Controls**")
                    btn_grasp = gr.Button("🤏 Grasp (Close)", variant="secondary")
                    btn_release = gr.Button("🖐️ Release (Open)", variant="secondary")

                # Status display for button actions
                btn_status = gr.Textbox(
                    label="Action Status",
                    value="Ready",
                    interactive=False,
                    lines=2
                )

            # Right Panel: Chat Interface
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Natural Language Control")

                # Chat history
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=400,
                    show_label=True
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

        # Camera feed update
        camera_feed.stream(
            fn=get_latest_frame,
            inputs=[],
            outputs=camera_feed,
            every=0.1,
            show_progress=False
        )

        # Movement button handlers
        btn_up.click(fn=move_up, inputs=[], outputs=btn_status)
        btn_down.click(fn=move_down, inputs=[], outputs=btn_status)
        btn_left.click(fn=move_left, inputs=[], outputs=btn_status)
        btn_right.click(fn=move_right, inputs=[], outputs=btn_status)

        # Gripper button handlers
        btn_grasp.click(fn=grasp_action, inputs=[], outputs=btn_status)
        btn_release.click(fn=release_action, inputs=[], outputs=btn_status)

        # Chat interface handlers
        chat_submit.click(
            fn=process_chat_message,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_status]
        ).then(
            lambda: "",  # Clear input after sending
            inputs=[],
            outputs=chat_input
        )

        # Allow Enter key to submit
        chat_input.submit(
            fn=process_chat_message,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_status]
        ).then(
            lambda: "",  # Clear input after sending
            inputs=[],
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
