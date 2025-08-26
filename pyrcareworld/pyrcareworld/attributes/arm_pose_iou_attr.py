"""
ArmPoseIoUAttr - Python interface for Unity ArmPoseIoUAttr component

Provides arm pose IoU (Intersection over Union) calculation using capsule-based visualization.
Tracks arm joints and position markers to measure pose similarity.
"""

from typing import List, Dict, Any, Optional
from pyrcareworld.attributes.base_attr import BaseAttr


class ArmPoseIoUAttr(BaseAttr):
    """
    Arm pose IoU calculation attribute using capsule-based collision detection.
    
    Monitors and calculates the IoU between current arm pose and a recorded target pose.
    Uses position markers (_pos nodes) for precise capsule endpoint positioning.
    
    Example usage:
        # Setup - attach to robot arm
        arm = env.GetAttr(arm_id).SetType(ArmPoseIoUAttr)
        
        # Configure detection
        arm.set_calculation_interval(1.0)
        arm.set_capsule_radius(0.03)
        arm.set_show_current_arm_visualization(True)
        
        # Record target pose
        arm.record_current_as_target()
        env.step()
        
        # Get IoU data
        arm.get_current_iou()
        env.step()
        
        # Access results
        iou = arm.current_iou
        if iou > 0.8:
            print("Pose matched!")
    """
    
    def __init__(self, env, id: int, data: dict = {}):
        """
        Initialize arm pose IoU attribute.
        
        Args:
            env: RCareWorld environment instance
            id: Unique identifier for the GameObject
            data: Optional initialization data dictionary
        """
        super().__init__(env, id, data)
        self._iou_data: Dict[str, Any] = {}
        self._detection_info: Dict[str, Any] = {}
    
    def parse_message(self, data: dict):
        """
        Parse incoming data from Unity ArmPoseIoUAttr component.
        
        Args:
            data: Dictionary containing IoU measurement data from Unity
        """
        super().parse_message(data)
        
        # Store IoU data if received
        if "current_iou" in data:
            self._iou_data["current_iou"] = data["current_iou"]
            
        # Store detection info if received
        if "detection_info" in data:
            self._detection_info = data["detection_info"]
            
        # Store joint detection info
        if "joint_detection_info" in data:
            self._detection_info = data["joint_detection_info"]
    
    # ===================  API Methods  ===================
    
    def record_current_as_target(self) -> None:
        """
        Record current arm pose as the target goal pose.
        
        Captures the current positions of shoulder, elbow, and wrist
        (using position markers if available) as the target pose.
        """
        self._send_data("RecordCurrentAsTarget")
    
    def clear_target(self) -> None:
        """
        Clear the recorded target pose.
        
        Removes the target pose and hides target visualization capsules.
        """
        self._send_data("ClearTarget")
    
    def set_calculation_interval(self, interval: float) -> None:
        """
        Set the IoU calculation interval.
        
        Args:
            interval: Time interval in seconds (minimum 0.1)
                     Controls how often IoU is calculated
        """
        if interval < 0.1:
            interval = 0.1
        self._send_data("SetCalculationInterval", interval)
    
    def set_enable_iou_calculation(self, enabled: bool) -> None:
        """
        Enable or disable IoU calculation.
        
        Args:
            enabled: True to enable calculation, False to disable
        """
        self._send_data("SetEnableIoUCalculation", enabled)
    
    def set_capsule_radius(self, radius: float) -> None:
        """
        Set capsule radius for visualization.
        
        Args:
            radius: Capsule radius in meters (minimum 0.01, default 0.03)
        """
        if radius < 0.01:
            radius = 0.01
        self._send_data("SetCapsuleRadius", radius)
    
    def get_current_iou(self) -> None:
        """
        Request immediate IoU calculation.
        
        Call env.step() after this method to receive the data.
        Result will be available through current_iou property.
        """
        self._send_data("GetCurrentIoU")
    
    def set_show_target_visualization(self, show: bool) -> None:
        """
        Toggle target pose visualization.
        
        Args:
            show: True to show red target capsules, False to hide
        """
        self._send_data("SetShowTargetVisualization", show)
    
    def set_show_current_arm_visualization(self, show: bool) -> None:
        """
        Toggle current arm visualization.
        
        Args:
            show: True to show blue current capsules, False to hide
        """
        self._send_data("SetShowCurrentArmVisualization", show)
    
    def set_show_position_markers(self, show: bool) -> None:
        """
        Toggle position marker visibility.
        
        Args:
            show: True to show position marker cubes, False to hide
        """
        self._send_data("SetShowPositionMarkers", show)
    
    def trigger_auto_detection(self) -> None:
        """
        Manually trigger auto-detection of joint objects and markers.
        
        Re-scans for shoulder, elbow, wrist joints and their _pos markers.
        """
        self._send_data("TriggerAutoDetection")
    
    def set_auto_detection_enabled(self, enabled: bool) -> None:
        """
        Enable or disable automatic joint detection.
        
        Args:
            enabled: True to enable auto-detection, False to disable
        """
        self._send_data("SetAutoDetectionEnabled", enabled)
    
    def set_auto_marker_detection_enabled(self, enabled: bool) -> None:
        """
        Enable or disable automatic marker detection.
        
        Args:
            enabled: True to enable marker detection, False to disable
        """
        self._send_data("SetAutoMarkerDetectionEnabled", enabled)
    
    def set_joint_replacement_enabled(self, enabled: bool) -> None:
        """
        Enable or disable joint replacement with capsules.
        
        Args:
            enabled: True to hide joints and show capsules, False to keep joints visible
        """
        self._send_data("SetJointReplacementEnabled", enabled)
    
    def get_detected_object_info(self) -> None:
        """
        Request information about detected joint and marker objects.
        
        Call env.step() after this method to receive the detection info.
        Results will be available through detection_info property.
        """
        self._send_data("GetDetectedObjectInfo")
    
    # ===================  Properties  ===================
    
    @property
    def current_iou(self) -> float:
        """
        Get current IoU value between current and target poses.
        
        Returns:
            IoU value between 0.0 and 1.0 (1.0 = perfect match)
        """
        return self.data.get("current_iou", 0.0)
    
    @property
    def has_target_pose(self) -> bool:
        """
        Check if a target pose has been recorded.
        
        Returns:
            True if target pose exists, False otherwise
        """
        return self.data.get("has_target_pose", False)
    
    @property
    def calculation_interval(self) -> float:
        """
        Get current IoU calculation interval.
        
        Returns:
            Calculation interval in seconds
        """
        return self.data.get("calculation_interval", 1.0)
    
    @property
    def capsule_radius(self) -> float:
        """
        Get current capsule radius.
        
        Returns:
            Capsule radius in meters
        """
        return self.data.get("capsule_radius", 0.03)
    
    @property
    def current_shoulder_position(self) -> List[float]:
        """
        Get current shoulder position (using marker if available).
        
        Returns:
            List [x, y, z] in world coordinates
        """
        return self.data.get("current_shoulder_position", [0.0, 0.0, 0.0])
    
    @property
    def current_elbow_position(self) -> List[float]:
        """
        Get current elbow position (using marker if available).
        
        Returns:
            List [x, y, z] in world coordinates
        """
        return self.data.get("current_elbow_position", [0.0, 0.0, 0.0])
    
    @property
    def current_wrist_position(self) -> List[float]:
        """
        Get current wrist position (using marker if available).
        
        Returns:
            List [x, y, z] in world coordinates
        """
        return self.data.get("current_wrist_position", [0.0, 0.0, 0.0])
    
    @property
    def target_shoulder_position(self) -> Optional[List[float]]:
        """
        Get target shoulder position if recorded.
        
        Returns:
            List [x, y, z] in world coordinates, or None if no target
        """
        if not self.has_target_pose:
            return None
        return self.data.get("target_shoulder_position", [0.0, 0.0, 0.0])
    
    @property
    def target_elbow_position(self) -> Optional[List[float]]:
        """
        Get target elbow position if recorded.
        
        Returns:
            List [x, y, z] in world coordinates, or None if no target
        """
        if not self.has_target_pose:
            return None
        return self.data.get("target_elbow_position", [0.0, 0.0, 0.0])
    
    @property
    def target_wrist_position(self) -> Optional[List[float]]:
        """
        Get target wrist position if recorded.
        
        Returns:
            List [x, y, z] in world coordinates, or None if no target
        """
        if not self.has_target_pose:
            return None
        return self.data.get("target_wrist_position", [0.0, 0.0, 0.0])
    
    @property
    def detected_joint_count(self) -> int:
        """
        Get number of detected joint objects.
        
        Returns:
            Number of detected joints (shoulder, elbow, wrist)
        """
        return self.data.get("detected_joint_objects_count", 0)
    
    @property
    def detected_marker_count(self) -> int:
        """
        Get number of detected position markers.
        
        Returns:
            Number of detected _pos markers
        """
        return self.data.get("detected_marker_objects_count", 0)
    
    @property
    def has_shoulder_marker(self) -> bool:
        """
        Check if shoulder position marker is available.
        
        Returns:
            True if right_shoulder_pos found, False otherwise
        """
        return self.data.get("has_shoulder_marker", False)
    
    @property
    def has_elbow_marker(self) -> bool:
        """
        Check if elbow position marker is available.
        
        Returns:
            True if right_elbow_pos found, False otherwise
        """
        return self.data.get("has_elbow_marker", False)
    
    @property
    def has_wrist_marker(self) -> bool:
        """
        Check if wrist position marker is available.
        
        Returns:
            True if right_wrist_pos found, False otherwise
        """
        return self.data.get("has_wrist_marker", False)
    
    @property
    def detection_info(self) -> Dict[str, Any]:
        """
        Get detailed detection information.
        
        Returns:
            Dictionary containing detected joint and marker names
        """
        return self._detection_info
    
    # ===================  Convenience Methods  ===================
    
    def get_pose_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of current pose state.
        
        Returns:
            Dictionary containing all pose-related data
        """
        return {
            "current_iou": self.current_iou,
            "has_target_pose": self.has_target_pose,
            "current_positions": {
                "shoulder": self.current_shoulder_position,
                "elbow": self.current_elbow_position,
                "wrist": self.current_wrist_position
            },
            "target_positions": {
                "shoulder": self.target_shoulder_position,
                "elbow": self.target_elbow_position,
                "wrist": self.target_wrist_position
            } if self.has_target_pose else None,
            "markers_available": {
                "shoulder": self.has_shoulder_marker,
                "elbow": self.has_elbow_marker,
                "wrist": self.has_wrist_marker
            },
            "detection_counts": {
                "joints": self.detected_joint_count,
                "markers": self.detected_marker_count
            }
        }
    
    def is_pose_matched(self, threshold: float = 0.8) -> bool:
        """
        Check if current pose matches target within threshold.
        
        Args:
            threshold: IoU threshold for considering a match (0.0-1.0)
            
        Returns:
            True if IoU is above threshold, False otherwise
        """
        return self.current_iou >= threshold
    
    def get_arm_lengths(self) -> Dict[str, float]:
        """
        Get current and target arm segment lengths.
        
        Returns:
            Dictionary with upper_arm and forearm lengths for current/target
        """
        result = {}
        
        if "current_upper_arm_length" in self.data:
            result["current_upper_arm"] = self.data["current_upper_arm_length"]
        if "current_forearm_length" in self.data:
            result["current_forearm"] = self.data["current_forearm_length"]
            
        if self.has_target_pose:
            if "target_upper_arm_length" in self.data:
                result["target_upper_arm"] = self.data["target_upper_arm_length"]
            if "target_forearm_length" in self.data:
                result["target_forearm"] = self.data["target_forearm_length"]
                
        return result