#!/usr/bin/env python3
"""Real-time Arm Pose IoU Monitor

This script monitors and displays the IoU between current arm pose and target pose
using the ArmPoseIoUAttr component in Unity through RCareWorld.

Usage:
    python test_arm_pose_iou.py

Requirements:
    - Unity Editor running with RCareWorld
    - Object with ArmPoseIoUAttr component attached
"""

import sys
import time
import numpy as np
from typing import Optional, List, Tuple

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.arm_pose_iou_attr import ArmPoseIoUAttr


class PoseMonitor:
    """Monitor for arm pose IoU calculations."""
    
    def __init__(self):
        """Initialize the pose monitor."""
        self.target_recorded = False
        self.step_count = 0
        self.iou_history = []
        
    def print_pose_status(self, arm_attr: ArmPoseIoUAttr) -> None:
        """Print current pose status and IoU information.
        
        Args:
            arm_attr: The ArmPoseIoUAttr instance
        """
        # Get current positions
        shoulder_pos = arm_attr.current_shoulder_position
        elbow_pos = arm_attr.current_elbow_position
        wrist_pos = arm_attr.current_wrist_position
        
        # Get current IoU
        current_iou = arm_attr.current_iou
        
        print(f"\n[Step {self.step_count}] Arm Pose Status")
        print("-" * 50)
        
        # Print current positions
        print("Current Positions:")
        print(f"  Shoulder: [{shoulder_pos[0]:.3f}, {shoulder_pos[1]:.3f}, {shoulder_pos[2]:.3f}]")
        print(f"  Elbow:    [{elbow_pos[0]:.3f}, {elbow_pos[1]:.3f}, {elbow_pos[2]:.3f}]")
        print(f"  Wrist:    [{wrist_pos[0]:.3f}, {wrist_pos[1]:.3f}, {wrist_pos[2]:.3f}]")
        
        # Print target positions if available
        if arm_attr.has_target_pose:
            target_shoulder = arm_attr.target_shoulder_position
            target_elbow = arm_attr.target_elbow_position
            target_wrist = arm_attr.target_wrist_position
            
            print("\nTarget Positions:")
            print(f"  Shoulder: [{target_shoulder[0]:.3f}, {target_shoulder[1]:.3f}, {target_shoulder[2]:.3f}]")
            print(f"  Elbow:    [{target_elbow[0]:.3f}, {target_elbow[1]:.3f}, {target_elbow[2]:.3f}]")
            print(f"  Wrist:    [{target_wrist[0]:.3f}, {target_wrist[1]:.3f}, {target_wrist[2]:.3f}]")
            
            # Print IoU
            print(f"\nIoU Score: {current_iou:.4f}")
            
            # Check if pose is matched
            if arm_attr.is_pose_matched(threshold=0.8):
                print("✓ Pose MATCHED! (IoU > 0.8)")
            else:
                print(f"✗ Pose not matched (need IoU > 0.8)")
        else:
            print("\n[No target pose recorded]")
        
        # Print marker availability
        print(f"\nPosition Markers Available:")
        print(f"  Shoulder: {'✓' if arm_attr.has_shoulder_marker else '✗'}")
        print(f"  Elbow:    {'✓' if arm_attr.has_elbow_marker else '✗'}")
        print(f"  Wrist:    {'✓' if arm_attr.has_wrist_marker else '✗'}")
        
    def print_statistics(self) -> None:
        """Print IoU statistics."""
        if len(self.iou_history) > 0:
            print("\n" + "=" * 50)
            print("IoU Statistics:")
            print(f"  Average IoU: {np.mean(self.iou_history):.4f}")
            print(f"  Max IoU:     {np.max(self.iou_history):.4f}")
            print(f"  Min IoU:     {np.min(self.iou_history):.4f}")
            print(f"  Std Dev:     {np.std(self.iou_history):.4f}")
            print("=" * 50)


def main() -> None:
    """Main execution function for arm pose IoU monitoring."""
    
    # Configuration
    USE_REMOTE = True          # Set to True to bind to specific address
    BIND_ADDRESS = "0.0.0.0"    # Address to bind server (0.0.0.0 for all interfaces)
    PORT = 5004                 # RCareWorld port
    TARGET_ID = 250826          # Unity object ID with ArmPoseIoUAttr
    UPDATE_INTERVAL = 0.001       # Seconds between updates
    RECORD_TARGET_AT_STEP = 10  # Step to record target pose
    
    # Initialize RCareWorld environment
    if USE_REMOTE:
        # Bind to specific address for remote connections
        env = RCareWorld(
            bind_address=BIND_ADDRESS,
            port=PORT
        )
        print(f"Server listening on {BIND_ADDRESS}:{PORT}")
    else:
        # Local Unity Editor connection (default)
        env = RCareWorld()
        print("Connecting to local Unity Editor")
    
    # Initialize monitor
    monitor = PoseMonitor()
    
    try:
        # Configure arm pose IoU attribute
        arm = env.GetAttr(TARGET_ID).SetType(ArmPoseIoUAttr)
        
        # Configure settings
        arm.set_calculation_interval(0.5)
        arm.set_capsule_radius(0.03)
        arm.set_enable_iou_calculation(True)
        arm.set_show_current_arm_visualization(True)
        arm.set_show_target_visualization(True)
        arm.set_show_position_markers(False)
        
        # Trigger auto-detection
        arm.trigger_auto_detection()
        env.step()
        
        # Get detection info
        arm.get_detected_object_info()
        env.step()
        
        print("=== Arm Pose IoU Monitor Started ===")
        print("Configuration:")
        print(f"  - Object ID: {TARGET_ID}")
        print(f"  - Update Interval: {UPDATE_INTERVAL}s")
        print(f"  - Capsule Radius: 0.03m")
        print(f"  - Target will be recorded at step {RECORD_TARGET_AT_STEP}")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        start_time = time.time()
        
        while True:
            # Record target pose at specified step
            if monitor.step_count == RECORD_TARGET_AT_STEP and not monitor.target_recorded:
                print(f"\n{'='*50}")
                print("RECORDING CURRENT POSE AS TARGET!")
                print(f"{'='*50}")
                arm.record_current_as_target()
                env.step()
                monitor.target_recorded = True
                time.sleep(1)  # Brief pause for emphasis
            
            # Always step to update data
            env.step()
            
            # Print status
            monitor.print_pose_status(arm)
            
            # Store IoU history if target exists
            if arm.has_target_pose:
                monitor.iou_history.append(arm.current_iou)
            
            monitor.step_count += 1
            
            # Print statistics every 20 steps
            if monitor.step_count % 20 == 0 and len(monitor.iou_history) > 0:
                monitor.print_statistics()
            
            # Control update frequency
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n=== Monitor Stopped by User ===")
        
        # Print final statistics
        if len(monitor.iou_history) > 0:
            monitor.print_statistics()
        
        # Clear target before closing
        if monitor.target_recorded:
            print("Clearing target pose...")
            arm.clear_target()
            env.step()
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting checklist:")
        print("  1. Is Unity Editor playing?")
        print("  2. Does the object ID exist in the scene?")
        print("  3. Is ArmPoseIoUAttr attached to the object?")
        print("  4. Are joints properly configured (shoulder, elbow, wrist)?")
        print("  5. Check if position markers (_pos) are present")
        
    finally:
        env.close()
        print("Cleanup completed")


if __name__ == "__main__":
    main()