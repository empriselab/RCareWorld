#!/usr/bin/env python3
"""
Official Test Script for LLM-Controlled Kinova Robot
====================================================

This test script creates a controlled test scene with:
- Kinova Gen3 robot with Robotiq 85 gripper
- Two Rigidbody boxes at fixed positions
- Full LLM and Gradio interface support

Usage:
    python -m rcg.test                    # Launch with Gradio (default)
    python -m rcg.test --no-gradio        # Launch terminal only
    python -m rcg.test --gradio-port 8080 # Custom Gradio port
    python -m rcg.test --share            # Create public Gradio link
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr
from rcg import llm
from rcg import gradio


# ============================================================================
# Interactive Terminal
# ============================================================================

def run_interactive_terminal(llm_controller):
    """Run interactive terminal loop."""

    print("\n" + "="*70)
    print("KINOVA ROBOT CONTROL - Interactive Terminal")
    print("="*70)
    print("\nMode: LLM-Assisted (Natural Language)")
    print("\nCommands:")
    print("  - Type your command in natural language and press Enter")
    print("  - Type 'help' to see example commands")
    print("  - Type 'reset' to reset conversation history")
    print("  - Type 'exit' or 'quit' to stop")
    print("="*70 + "\n")

    running = True

    while running:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nExiting...")
                running = False
                continue

            if user_input.lower() == "help":
                print("\n" + "="*70)
                print("EXAMPLE COMMANDS")
                print("="*70)
                print("\n  - Show me all objects in the scene")
                print("  - Where is the box?")
                print("  - Move to box1")
                print("  - Move 20cm above the box")
                print("  - Grasp the box")
                print("  - Release the object")
                print("  - Move to position x=0.5, y=0.3, z=0.2")
                print("  - Move 10cm up (relative movement)")
                print("="*70 + "\n")
                continue

            if user_input.lower() == "reset":
                llm_controller.reset()
                continue

            # Process command with LLM
            print(f"\n[Processing] {user_input}")
            result = llm_controller.process_command(user_input)

            if result["success"]:
                # Display function result
                if result.get("function_called"):
                    func_result = result.get("function_result", {})

                    print(f"\n[Function] {result['function_called']}")
                    if func_result.get("success"):
                        print(f"[Success] {func_result.get('message', 'Done')}")
                    else:
                        print(f"[Failed] {func_result.get('message', 'Unknown error')}")

                # Display LLM response
                print(f"\n[Assistant] {result['llm_response']}")
            else:
                print(f"\n[Error] {result.get('error', 'Unknown error')}")

            print()  # Blank line

        except KeyboardInterrupt:
            print("\n\nInterrupted by user (Ctrl+C)")
            running = False

        except EOFError:
            print("\n\nEnd of input")
            running = False

        except Exception as e:
            print(f"\n[Error] {str(e)}")
            import traceback
            traceback.print_exc()


# ============================================================================
# Test Scene Setup
# ============================================================================

def setup_test_scene(env):
    """
    Setup the test scene with Kinova robot and boxes.

    Scene configuration matches example_kinova_gen3_move.py:
    - Kinova Gen3 robot at origin
    - Two Rigidbody boxes at fixed positions

    Returns:
        tuple: (robot, gripper, camera) attributes
    """
    print("[Scene] Creating test objects...")

    # Create Kinova robot
    robot = env.InstanceObject(
        name="kinova_gen3_robotiq85",
        id=123456,
        attr_type=attr.ControllerAttr
    )
    robot.SetPosition([0, 0, 0])

    # Create camera for Gradio
    camera = env.InstanceObject(
        name="Camera",
        id=888888,
        attr_type=attr.CameraAttr
    )
    camera.SetTransform(position=[0, 0.5, -1], rotation=[15, 0, 0])

    # Wait for robot to stabilize
    env.step(500)

    # Get gripper (ID is robot_id + 0)
    gripper = env.GetAttr(1234560)
    gripper.GripperOpen()

    # Set initial robot pose
    robot.IKTargetDoMove(position=[0, 0.5, 0.5], duration=0, speed_based=False)
    robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)
    robot.WaitDo()

    # Create two test boxes at fixed positions
    box1 = env.InstanceObject(
        name="Rigidbody_Box",
        id=111111,
        attr_type=attr.RigidbodyAttr
    )
    box1.SetTransform(
        position=[-0.4, 0.03, 0.4],
        scale=[0.06, 0.06, 0.06]
    )

    box2 = env.InstanceObject(
        name="Rigidbody_Box",
        id=222222,
        attr_type=attr.RigidbodyAttr
    )
    box2.SetTransform(
        position=[0.4, 0.03, 0.4],
        scale=[0.06, 0.06, 0.06]
    )

    # Wait for boxes to settle
    env.step(100)

    print("[Scene] Test scene ready:")
    print(f"  - Kinova robot at origin")
    print(f"  - Box 1 at position [-0.4, 0.03, 0.4]")
    print(f"  - Box 2 at position [0.4, 0.03, 0.4]")
    print(f"  - Camera at [0, 0.5, -1]")

    return robot, gripper, camera


# ============================================================================
# Main Entry Point
# ============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test script for LLM-Controlled Kinova Robot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m rcg.test                    # Launch with Gradio (default)
  python -m rcg.test --no-gradio        # Terminal mode only
  python -m rcg.test --gradio-port 8080 # Custom port
  python -m rcg.test --share            # Create public link
        """
    )

    parser.add_argument(
        "--no-gradio",
        action="store_true",
        help="Disable Gradio interface and use terminal only"
    )

    parser.add_argument(
        "--gradio-port",
        type=int,
        default=7860,
        help="Port for Gradio server (default: 7860)"
    )

    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio link (requires --gradio enabled)"
    )

    parser.add_argument(
        "--unity-port",
        type=int,
        default=5004,
        help="Unity connection port (default: 5004)"
    )

    return parser.parse_args()


def main():
    """Main entry point for test script."""

    # Parse arguments
    args = parse_args()
    use_gradio = not args.no_gradio

    print("\n" + "="*70)
    print("KINOVA ROBOT TEST ENVIRONMENT - STARTING")
    print("="*70)
    print(f"Mode: {'Gradio Web Interface' if use_gradio else 'Terminal Only'}")
    print("="*70 + "\n")

    # Step 1: Initialize environment with test scene assets
    print("[1/4] Initializing test environment...")
    try:
        env = RCareWorld(
            assets=["kinova_gen3_robotiq85", "Camera"],
            executable_file="@editor",
            graphics=True
        )
        env.SetTimeStep(0.005)
        print("[Success] Environment initialized")
    except Exception as e:
        print(f"[Error] Failed to initialize environment: {e}")
        print("\nMake sure:")
        print("  1. Unity Editor is running")
        print("  2. Press Play in Unity Editor")
        return

    # Step 2: Setup test scene (robot + boxes)
    print("\n[2/4] Setting up test scene...")
    try:
        robot, gripper, camera = setup_test_scene(env)
        print("[Success] Test scene ready")
    except Exception as e:
        print(f"[Error] Failed to setup scene: {e}")
        import traceback
        traceback.print_exc()
        env.close()
        return

    # Step 3: Initialize LLM
    print("\n[3/4] Initializing LLM controller...")
    try:
        # Initialize LLM functions
        llm.initialize(env, robot, gripper)

        # Create LLM controller
        llm_controller = llm.LLMController()
        print("[Success] LLM controller initialized")
    except Exception as e:
        print(f"[Error] Failed to initialize LLM: {e}")
        print("\nMake sure:")
        print("  1. OpenAI package installed: pip install openai")
        print("  2. OPENAI_API_KEY is set: export OPENAI_API_KEY=\"sk-...\"")
        env.close()
        return

    # Print scene info
    print("\n" + "="*70)
    print("SCENE INFORMATION")
    print("="*70)
    print(f"Total objects: {len(env.attrs)}")
    for obj_id, obj_attr in env.attrs.items():
        obj_name = obj_attr.data.get("name", "Unknown")
        obj_pos = obj_attr.data.get("position", [0, 0, 0])
        print(f"  - {obj_name} (ID: {obj_id}) at {obj_pos}")
    print("="*70 + "\n")

    # Step 4: Launch interface
    try:
        if use_gradio:
            print("[4/4] Initializing Gradio interface...")
            gradio.initialize(env, robot, gripper, camera, llm_controller)
            print("[Success] Gradio initialized")

            print("\n[Ready] Launching Gradio web interface...\n")
            gradio.launch_interface(share=args.share, server_port=args.gradio_port)
        else:
            print("[4/4] Skipping Gradio (terminal mode)")
            print("\n[Ready] Starting interactive terminal...\n")
            run_interactive_terminal(llm_controller)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n[Error] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[Cleanup] Closing environment...")
        if use_gradio:
            gradio.stop_camera_feed()
        env.close()
        print("[Done] Goodbye!\n")


if __name__ == "__main__":
    main()
