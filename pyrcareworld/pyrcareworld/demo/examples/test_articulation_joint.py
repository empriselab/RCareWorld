#!/usr/bin/env python3
"""Simple Joint Control Test Script.

This script provides basic testing of Unity ArticulatedJointAttr components:
1. Random pose testing (10 times)
2. Manual user input control

Usage:
    python joint_test_simple.py

Requirements:
    - Unity Editor running with RCareWorld
    - Object with ArticulatedJointAttr component attached
"""

import sys
import time

<<<<<<< HEAD
# # Add RCareWorld to Python path - modify as needed
# sys.path.append('/home/dell/github/rcarew/pyrcareworld')

=======
>>>>>>> 397045b607452c2e6d799be3c96243509c779797
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.articulated_joint_attr import ArticulatedJointAttr


def test_randomization(joint_ctrl: ArticulatedJointAttr) -> None:
    """Test joint randomization 10 times with 2 second intervals.
    
    Args:
        joint_ctrl: ArticulatedJointAttr instance to control
    """
    print("=== Random Pose Testing (10 times) ===")
    
    for i in range(10):
        print(f"Random pose {i+1}/10:")
        
        # Get state before randomization
        joint_ctrl.env.step()
        before_pose = joint_ctrl.get_pose_summary()
        shoulder_before = before_pose['current_shoulder']
        elbow_before = before_pose['current_elbow']
        
        print(f"  Before: Shoulder({shoulder_before[0]:.1f}°, {shoulder_before[1]:.1f}°) "
              f"Elbow({elbow_before:.1f}°)")
        
        # Trigger randomization
        joint_ctrl.trigger_randomization()
        time.sleep(5.0)  # Wait 2 seconds
        
        # Get state after randomization
        joint_ctrl.env.step()
        after_pose = joint_ctrl.get_pose_summary()
        shoulder_after = after_pose['current_shoulder']
        elbow_after = after_pose['current_elbow']
        
        print(f"  After:  Shoulder({shoulder_after[0]:.1f}°, {shoulder_after[1]:.1f}°) "
              f"Elbow({elbow_after:.1f}°)")
        print()
    
    print("Random testing complete!\n")


def manual_control(joint_ctrl: ArticulatedJointAttr) -> None:
    """Manual control mode where user inputs target angles.
    
    Args:
        joint_ctrl: ArticulatedJointAttr instance to control
    """
    print("=== Manual Control Mode ===")
    print("Joint Limits:")
    print("  Shoulder X: -5° to 75°")
    print("  Shoulder Y: -180° to 90°")
    print("  Elbow: -90° to 0°")
    print()
    print("Commands:")
    print("  Enter three numbers: <shoulder_x> <shoulder_y> <elbow>")
    print("  Example: 30 45 -60")
    print("  Type 'q' to quit")
    print("  Type 's' to show current angles")
    print("  Type 'r' to randomize")
    print()
    
    while True:
        try:
            user_input = input("Enter angles (or command): ").strip()
            
            if user_input.lower() == 'q':
                print("Exiting manual control")
                break
            
            elif user_input.lower() == 's':
                # Show current status
                joint_ctrl.env.step()
                pose = joint_ctrl.get_pose_summary()
                shoulder = pose['current_shoulder']
                elbow = pose['current_elbow']
                print(f"Current angles: Shoulder({shoulder[0]:.1f}°, {shoulder[1]:.1f}°) "
                      f"Elbow({elbow:.1f}°)")
                print()
                continue
            
            elif user_input.lower() == 'r':
                # Randomize
                print("Randomizing...")
                joint_ctrl.trigger_randomization()
                time.sleep(2.0)
                joint_ctrl.env.step()
                pose = joint_ctrl.get_pose_summary()
                shoulder = pose['current_shoulder']
                elbow = pose['current_elbow']
                print(f"New random pose: Shoulder({shoulder[0]:.1f}°, {shoulder[1]:.1f}°) "
                      f"Elbow({elbow:.1f}°)")
                print()
                continue
            
            # Parse three numbers
            parts = user_input.split()
            if len(parts) != 3:
                print("Please enter exactly 3 numbers: <shoulder_x> <shoulder_y> <elbow>")
                continue
            
            try:
                shoulder_x = float(parts[0])
                shoulder_y = float(parts[1])
                elbow = float(parts[2])
            except ValueError:
                print("Invalid numbers. Please enter valid decimal numbers.")
                continue
            
            # Validate angles
            is_valid, error_msg = joint_ctrl.validate_angles(shoulder_x, shoulder_y, elbow)
            if not is_valid:
                print(f"Warning: {error_msg}")
                print("Values will be automatically clamped to valid ranges.")
            
            # Move to target
            print(f"Moving to: Shoulder({shoulder_x}°, {shoulder_y}°) Elbow({elbow}°)")
            joint_ctrl.move_to_pose(shoulder_x, shoulder_y, elbow)
            
            # Wait a moment and show result
            time.sleep(3.0)
            joint_ctrl.env.step()
            pose = joint_ctrl.get_pose_summary()
            final_shoulder = pose['current_shoulder']
            final_elbow = pose['current_elbow']
            
            print(f"Reached: Shoulder({final_shoulder[0]:.1f}°, {final_shoulder[1]:.1f}°) "
                  f"Elbow({final_elbow:.1f}°)")
            print()
            
        except KeyboardInterrupt:
            print("\nManual control interrupted")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")


def main() -> None:
    """Main execution function."""
    # Configuration
    TARGET_ID = 250823  # Unity object ID to control
    USE_REMOTE = False
    
    print("Initializing RCareWorld environment...")
<<<<<<< HEAD
    env = RCareWorld()
        # bind_address="0.0.0.0",
        # remote_mode=True,
        # port=5004
    # )
=======
    if USE_REMOTE:
        env = RCareWorld(
            bind_address="0.0.0.0",
                remote_mode=True,
                port=5004
            )
    else:
        env = RCareWorld()
>>>>>>> 397045b607452c2e6d799be3c96243509c779797
    
    try:
        # Setup joint control
        print(f"Setting up joint control for object ID: {TARGET_ID}")
        joint_ctrl = env.GetAttr(TARGET_ID).SetType(ArticulatedJointAttr)
        
        # Enable control
        joint_ctrl.set_control_enabled(True)
        joint_ctrl.set_log_interval(0.001)
        
        print("Connection established!")
        print("=== Simple Joint Control Test ===")
        
        # Wait for initial connection
        for i in range(3):
            env.step()
            time.sleep(0.2)
        
        # Run random testing
        test_randomization(joint_ctrl)
        
        # Start manual control
        manual_control(joint_ctrl)
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Troubleshooting:")
        print("  1. Is Unity Editor playing?")
        print("  2. Does the object ID exist?")
        print("  3. Is ArticulatedJointAttr attached?")
        
    finally:
        env.close()
        print("Cleanup completed")


if __name__ == "__main__":
    main()