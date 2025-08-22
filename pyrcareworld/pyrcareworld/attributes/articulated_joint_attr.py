"""
ArticulatedJointAttr - Python interface for Unity ArticulatedJointAttr component

Provides real-time control and monitoring of articulated body joints in Unity
through RCareWorld's TCP communication system. Supports shoulder (3 DOF spherical)
and elbow (1 DOF revolute) joint control with randomization capabilities.
"""

from typing import List, Dict, Any, Optional, Tuple
from pyrcareworld.attributes.base_attr import BaseAttr


class ArticulatedJointAttr(BaseAttr):
    """
    Articulated joint control attribute for Unity ArticulationBody components.
    
    Enables precise control of robotic arm joints with real-time position feedback,
    automatic randomization, and comprehensive monitoring capabilities. Designed
    for human-like joint configurations with anatomically correct limits.
    
    Joint Configuration:
        - Shoulder: 3 DOF spherical joint (X: -5° to 75°, Y: -180° to 90°, Z: locked at 0°)
        - Elbow: 1 DOF revolute joint (-90° to 0°)
    
    Example usage:
        # Setup joint control
        joint_ctrl = env.GetAttr(joint_id).SetType(ArticulatedJointAttr)
        
        # Configure control parameters
        joint_ctrl.set_log_interval(0.2)
        joint_ctrl.set_control_enabled(True)
        
        # Move to specific pose
        joint_ctrl.move_to_pose(shoulder_x=30, shoulder_y=45, elbow=-60)
        
        # Monitor real-time data
        angles = joint_ctrl.get_current_angles()
        print(f"Current angles: {angles}")
        
        # Randomize joint positions
        joint_ctrl.trigger_randomization()
    """
    
    def __init__(self, env, id: int, data: dict = {}):
        """
        Initialize articulated joint attribute.
        
        Args:
            env: RCareWorld environment instance
            id: Unique identifier for the GameObject with ArticulatedJointAttr
            data: Optional initialization data dictionary
        """
        super().__init__(env, id, data)
        
        # Store joint angle data received from Unity
        self._joint_angles_data: Dict[str, Any] = {}
        
        # Joint limits matching Unity component constraints
        self.shoulder_x_limits = (-5.0, 75.0)
        self.shoulder_y_limits = (-180.0, 90.0)
        self.shoulder_z_limits = (0.0, 0.0)  # Locked axis
        self.elbow_limits = (-90.0, 0.0)
    
    def parse_message(self, data: dict):
        """
        Parse incoming data from Unity ArticulatedJointAttr component.
        
        Processes real-time joint angle data, control state, and configuration
        information transmitted continuously from Unity's AddPermanentData().
        
        Args:
            data: Dictionary containing joint data from Unity with keys:
                - 'shoulder_angles': List [x, y, z] of current shoulder angles
                - 'elbow_angle': Current elbow angle in degrees
                - 'control_enabled': Whether joint control is active
                - 'log_interval': Current update interval in seconds
                - 'target_shoulder_x': Target X angle for shoulder
                - 'target_shoulder_y': Target Y angle for shoulder  
                - 'target_elbow': Target angle for elbow
                - 'initialize_with_random': Random initialization setting
                - 'joint_angles': Response data from GetCurrentJointAngles()
        """
        super().parse_message(data)
        
        # Store joint angles response data if received
        if "joint_angles" in data:
            self._joint_angles_data = data["joint_angles"]
    
    # ==================== API Methods ====================
    
    def set_shoulder_targets(self, x: float, y: float) -> None:
        """
        Set target angles for shoulder joint X and Y axes.
        
        The Z axis is automatically locked to 0 degrees and cannot be modified.
        Values are automatically clamped to valid ranges if outside limits.
        
        Args:
            x: Target X angle in degrees (-5.0 to 75.0)
            y: Target Y angle in degrees (-180.0 to 90.0)
        """
        # Validate and clamp inputs to valid ranges
        x_clamped = max(self.shoulder_x_limits[0], min(self.shoulder_x_limits[1], x))
        y_clamped = max(self.shoulder_y_limits[0], min(self.shoulder_y_limits[1], y))
        
        # Warn user if values were clamped
        if x != x_clamped:
            print(f"Warning: Shoulder X angle {x}° clamped to {x_clamped}°")
        if y != y_clamped:
            print(f"Warning: Shoulder Y angle {y}° clamped to {y_clamped}°")
        
        # Send command to Unity
        self._send_data("SetShoulderTargets", x_clamped, y_clamped)
    
    def set_elbow_target(self, angle: float) -> None:
        """
        Set target angle for elbow joint.
        
        Args:
            angle: Target angle in degrees (-90.0 to 0.0)
                  -90° represents fully bent, 0° represents fully extended
        """
        # Validate and clamp input to valid range
        angle_clamped = max(self.elbow_limits[0], min(self.elbow_limits[1], angle))
        
        # Warn user if value was clamped
        if angle != angle_clamped:
            print(f"Warning: Elbow angle {angle}° clamped to {angle_clamped}°")
        
        # Send command to Unity
        self._send_data("SetElbowTarget", angle_clamped)
    
    def set_control_enabled(self, enabled: bool) -> None:
        """
        Enable or disable joint control system.
        
        When enabled, joints will actively move to their target positions.
        When disabled, joints maintain their current positions but do not
        respond to new target commands.
        
        Args:
            enabled: True to enable joint control, False to disable
        """
        self._send_data("SetControlEnabled", enabled)
    
    def set_log_interval(self, interval: float) -> None:
        """
        Set the data logging and update interval.
        
        Controls how frequently Unity updates joint data and applies control
        commands. Lower values provide more responsive control but increase
        computational overhead.
        
        Args:
            interval: Update interval in seconds (minimum 0.1)
        """
        interval_clamped = max(0.1, interval)
        if interval != interval_clamped:
            print(f"Warning: Log interval {interval}s clamped to {interval_clamped}s")
            
        self._send_data("SetLogInterval", interval_clamped)
    
    def trigger_randomization(self) -> None:
        """
        Trigger immediate randomization of all joint angles.
        
        Generates random angles within valid ranges for all joints and applies
        them immediately. This action temporarily enables control if it was
        disabled, applies the random angles, then restores the original state.
        """
        self._send_data("TriggerRandomization")
    
    def set_initialize_with_random(self, enabled: bool) -> None:
        """
        Set whether joints should be randomized on component startup.
        
        Args:
            enabled: True to enable automatic randomization on startup,
                    False to start with neutral positions
        """
        self._send_data("SetInitializeWithRandom", enabled)
    
    def get_current_joint_angles(self) -> None:
        """
        Request immediate joint angle data from Unity.
        
        Call env.step() after this method to receive the response data.
        Results will be available through the current_angles property.
        """
        self._send_data("GetCurrentJointAngles")
    
    def reset_to_neutral(self) -> None:
        """
        Reset all joints to neutral position (all angles to 0 degrees).
        
        This immediately sets all target angles to 0 and applies them if
        control is currently enabled.
        """
        self._send_data("ResetToNeutral")
    
    # ==================== Properties ====================
    
    @property
    def shoulder_angles(self) -> List[float]:
        """
        Get current shoulder joint angles for all three axes.
        
        Returns:
            List [x, y, z] of current shoulder angles in degrees
        """
        return self.data.get("shoulder_angles", [0.0, 0.0, 0.0])
    
    @property
    def elbow_angle(self) -> float:
        """
        Get current elbow joint angle.
        
        Returns:
            Current elbow angle in degrees
        """
        return self.data.get("elbow_angle", 0.0)
    
    @property
    def control_enabled(self) -> bool:
        """
        Check if joint control is currently enabled.
        
        Returns:
            True if control is active, False if disabled
        """
        return self.data.get("control_enabled", False)
    
    @property
    def log_interval(self) -> float:
        """
        Get current data logging interval.
        
        Returns:
            Current update interval in seconds
        """
        return self.data.get("log_interval", 0.5)
    
    @property
    def target_shoulder_x(self) -> float:
        """
        Get current target angle for shoulder X axis.
        
        Returns:
            Target shoulder X angle in degrees
        """
        return self.data.get("target_shoulder_x", 0.0)
    
    @property
    def target_shoulder_y(self) -> float:
        """
        Get current target angle for shoulder Y axis.
        
        Returns:
            Target shoulder Y angle in degrees
        """
        return self.data.get("target_shoulder_y", 0.0)
    
    @property
    def target_elbow(self) -> float:
        """
        Get current target angle for elbow joint.
        
        Returns:
            Target elbow angle in degrees
        """
        return self.data.get("target_elbow", 0.0)
    
    @property
    def initialize_with_random(self) -> bool:
        """
        Check if random initialization on startup is enabled.
        
        Returns:
            True if startup randomization is enabled, False otherwise
        """
        return self.data.get("initialize_with_random", True)
    
    @property
    def current_angles(self) -> Dict[str, float]:
        """
        Get current joint angles from immediate query response.
        
        This property returns data from the last GetCurrentJointAngles() call.
        Use get_current_joint_angles() followed by env.step() to update.
        
        Returns:
            Dictionary containing:
            {
                'shoulder_x': float,
                'shoulder_y': float,
                'shoulder_z': float,
                'elbow': float,
                'control_enabled': bool
            }
        """
        return self._joint_angles_data
    
    # ==================== Convenience Methods ====================
    
    def move_to_pose(self, shoulder_x: float, shoulder_y: float, elbow: float,
                     enable_control: bool = True) -> None:
        """
        Move joints to a specific pose configuration.
        
        This is a convenience method that sets all joint targets in a single
        operation and optionally enables control.
        
        Args:
            shoulder_x: Target shoulder X angle in degrees
            shoulder_y: Target shoulder Y angle in degrees
            elbow: Target elbow angle in degrees
            enable_control: Whether to enable control before moving
        """
        if enable_control:
            self.set_control_enabled(True)
        
        self.set_shoulder_targets(shoulder_x, shoulder_y)
        self.set_elbow_target(elbow)
        
        print(f"Moving to pose: Shoulder({shoulder_x:.1f}°, {shoulder_y:.1f}°) "
              f"Elbow({elbow:.1f}°)")
    
    def get_pose_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of current joint state.
        
        Returns:
            Dictionary containing current and target angles, control state,
            and configuration parameters:
            {
                'current_shoulder': [x, y, z],
                'current_elbow': float,
                'target_shoulder_x': float,
                'target_shoulder_y': float, 
                'target_elbow': float,
                'control_enabled': bool,
                'log_interval': float,
                'initialize_with_random': bool
            }
        """
        return {
            'current_shoulder': self.shoulder_angles,
            'current_elbow': self.elbow_angle,
            'target_shoulder_x': self.target_shoulder_x,
            'target_shoulder_y': self.target_shoulder_y,
            'target_elbow': self.target_elbow,
            'control_enabled': self.control_enabled,
            'log_interval': self.log_interval,
            'initialize_with_random': self.initialize_with_random
        }
    
    def validate_angles(self, shoulder_x: float, shoulder_y: float, 
                       elbow: float) -> Tuple[bool, str]:
        """
        Validate if given angles are within joint limits.
        
        Args:
            shoulder_x: Shoulder X angle to validate
            shoulder_y: Shoulder Y angle to validate
            elbow: Elbow angle to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            is_valid: True if all angles are valid, False otherwise
            error_message: Description of validation errors, empty if valid
        """
        errors = []
        
        if not (self.shoulder_x_limits[0] <= shoulder_x <= self.shoulder_x_limits[1]):
            errors.append(f"Shoulder X {shoulder_x}° outside range {self.shoulder_x_limits}")
            
        if not (self.shoulder_y_limits[0] <= shoulder_y <= self.shoulder_y_limits[1]):
            errors.append(f"Shoulder Y {shoulder_y}° outside range {self.shoulder_y_limits}")
            
        if not (self.elbow_limits[0] <= elbow <= self.elbow_limits[1]):
            errors.append(f"Elbow {elbow}° outside range {self.elbow_limits}")
            
        return len(errors) == 0, "; ".join(errors)
    
    def get_joint_limits(self) -> Dict[str, Tuple[float, float]]:
        """
        Get joint angle limits for all axes.
        
        Returns:
            Dictionary mapping joint names to (min, max) limit tuples:
            {
                'shoulder_x': (-5.0, 75.0),
                'shoulder_y': (-180.0, 90.0), 
                'shoulder_z': (0.0, 0.0),
                'elbow': (-90.0, 0.0)
            }
        """
        return {
            'shoulder_x': self.shoulder_x_limits,
            'shoulder_y': self.shoulder_y_limits,
            'shoulder_z': self.shoulder_z_limits,
            'elbow': self.elbow_limits
        }
    
    def is_at_target(self, tolerance: float = 1.0) -> bool:
        """
        Check if all joints are within tolerance of their target positions.
        
        Args:
            tolerance: Maximum angular difference in degrees to consider "at target"
            
        Returns:
            True if all joints are within tolerance of targets, False otherwise
        """
        shoulder_current = self.shoulder_angles
        
        # Check shoulder X and Y axes (Z is always locked to 0)
        shoulder_x_diff = abs(shoulder_current[0] - self.target_shoulder_x)
        shoulder_y_diff = abs(shoulder_current[1] - self.target_shoulder_y)
        elbow_diff = abs(self.elbow_angle - self.target_elbow)
        
        return (shoulder_x_diff <= tolerance and 
                shoulder_y_diff <= tolerance and 
                elbow_diff <= tolerance)
    
    def wait_for_target(self, timeout: float = 10.0, tolerance: float = 1.0) -> bool:
        """
        Wait for joints to reach their target positions.
        
        Args:
            timeout: Maximum time to wait in seconds
            tolerance: Angular tolerance in degrees
            
        Returns:
            True if targets reached within timeout, False if timeout occurred
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            self.env.step()
            if self.is_at_target(tolerance):
                return True
            time.sleep(0.05)  # Small delay to prevent excessive CPU usage
            
        return False