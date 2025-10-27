#!/usr/bin/env python3
"""
Main Entry Point for LLM-Controlled Kinova Robot
=================================================

Simplified main entry that:
1. Initializes Unity environment (keeps connection open)
2. Initializes LLM controller
3. Runs interactive terminal loop OR Gradio web interface

Usage:
    python -m rcg.main                    # Launch with Gradio (default)
    python -m rcg.main --no-gradio        # Launch terminal only
    python -m rcg.main --gradio-port 8080 # Custom Gradio port
    python -m rcg.main --share            # Create public Gradio link
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from rcg.env import KinovaTestEnv
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
                print("  - Where is the cube?")
                print("  - Move to the cube")
                print("  - Move 20cm above the cube")
                print("  - Grasp the cube")
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
# Main Entry Point
# ============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="LLM-Controlled Kinova Robot System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m rcg.main                    # Launch with Gradio (default)
  python -m rcg.main --no-gradio        # Terminal mode only
  python -m rcg.main --gradio-port 8080 # Custom port
  python -m rcg.main --share            # Create public link
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
    """Main entry point."""

    # Parse arguments
    args = parse_args()
    use_gradio = not args.no_gradio

    print("\n" + "="*70)
    print("KINOVA ROBOT LLM CONTROL SYSTEM - STARTING")
    print("="*70)
    print(f"Mode: {'Gradio Web Interface' if use_gradio else 'Terminal Only'}")
    print("="*70 + "\n")

    # Step 1: Initialize environment
    print("[1/4] Initializing Unity environment...")
    try:
        env = KinovaTestEnv(
            executable_file="@editor",
            graphics=True,
            port=args.unity_port
        )
        env.step(50)  # Wait for initialization
        print("[Success] Environment initialized")
    except Exception as e:
        print(f"[Error] Failed to initialize environment: {e}")
        print("\nMake sure:")
        print("  1. Unity Editor is running")
        print("  2. Kinova scene is open")
        print("  3. Press Play in Unity Editor")
        return

    # Step 2: Get robot, gripper, and camera
    print("\n[2/4] Connecting to robot, gripper, and camera...")
    try:
        robot = env.get_kinova()
        gripper = env.get_gripper()
        camera = env.get_camera()  # Camera needed for Gradio
        print("[Success] Robot, gripper, and camera connected")
    except Exception as e:
        print(f"[Error] Failed to connect: {e}")
        print("\nMake sure:")
        print("  1. Object IDs are configured in rcg/env.py")
        print("  2. Objects exist in Unity scene")
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
    env.print_scene_info()
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
