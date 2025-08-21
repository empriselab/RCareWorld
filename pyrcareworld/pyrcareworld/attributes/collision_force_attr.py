"""
CollisionForceAttr - Python interface for Unity CollisionForceAttr component

Provides contact force detection using velocity-based physics calculations.
Example: Attach to table in Unity, monitor when robot end-effector contacts it.
"""

from typing import List, Dict, Any, Optional
from pyrcareworld.attributes.base_attr import BaseAttr


class CollisionForceAttr(BaseAttr):
    """
    Contact force detection attribute using velocity-based physics calculations.
    
    Monitors impact forces when objects collide with the GameObject this attribute
    is attached to. Uses Newton's second law (F = m * Δv / Δt) for accurate
    force measurement.
    
    Example usage:
        # Setup - attach to table to monitor robot contact
        table = env.GetAttr(table_id).SetType(CollisionForceAttr)
        
        # Configure detection
        table.set_detection_interval(0.5)
        table.set_min_force_threshold(1.0) 
        table.set_enable_logging(True)
        
        # Get force data
        table.get_current_contact_force()
        env.step()
        
        # Access results
        if table.is_being_hit:
            force = table.total_impact_force
            direction = table.final_direction
            events = table.impact_events
    """
    
    def __init__(self, env, id: int, data: dict = {}):
        """
        Initialize collision force attribute.
        
        Args:
            env: RCareWorld environment instance
            id: Unique identifier for the GameObject
            data: Optional initialization data dictionary
        """
        super().__init__(env, id, data)
        self._impact_force_data: Dict[str, Any] = {}
    
    def parse_message(self, data: dict):
        """
        Parse incoming data from Unity CollisionForceAttr component.
        
        Args:
            data: Dictionary containing force measurement data from Unity
        """
        super().parse_message(data)
        
        # Store impact force data if received
        if "impact_force_data" in data:
            self._impact_force_data = data["impact_force_data"]
    
    # ===================  API Methods  ===================
    
    def get_current_contact_force(self) -> None:
        """
        Request immediate contact force data from Unity.
        
        Call env.step() after this method to receive the data.
        Results will be available through property accessors.
        """
        self._send_data("GetCurrentContactForce")
    
    def set_detection_interval(self, interval: float) -> None:
        """
        Set the time interval for force data logging.
        
        Args:
            interval: Time interval in seconds (minimum 0.1)
                     Controls how often Unity outputs force data to console
        """
        if interval < 0.1:
            interval = 0.1
        self._send_data("SetDetectionInterval", interval)
    
    def set_min_force_threshold(self, threshold: float) -> None:
        """
        Set minimum force threshold for filtering noise.
        
        Args:
            threshold: Force threshold in Newtons (minimum 0.0)
                      Forces below this value will be ignored
        """
        if threshold < 0.0:
            threshold = 0.0
        self._send_data("SetMinForceThreshold", threshold)
    
    def set_enable_logging(self, enable: bool) -> None:
        """
        Enable or disable Unity console logging.
        
        Args:
            enable: True to enable console output, False to disable
                   When enabled, Unity will log force data to console
        """
        self._send_data("SetEnableLogging", enable)
    
    # ===================  Properties  ===================
    
    @property
    def is_being_hit(self) -> bool:
        """
        Check if object is currently being impacted.
        
        Returns:
            True if any contact force is detected above threshold, False otherwise
        """
        return self._impact_force_data.get("is_being_hit", False)
    
    @property
    def total_impact_force(self) -> float:
        """
        Get total magnitude of impact force.
        
        Returns:
            Total force magnitude in Newtons from all contact points
        """
        return self._impact_force_data.get("total_impact_force", 0.0)
    
    @property
    def total_force_vector(self) -> List[float]:
        """
        Get 3D force vector from vector composition of all contact forces.
        
        Returns:
            List [x, y, z] representing the composite force vector in Newtons
        """
        return self._impact_force_data.get("total_force_vector", [0.0, 0.0, 0.0])
    
    @property
    def final_direction(self) -> List[float]:
        """
        Get normalized direction of the composite force.
        
        Returns:
            List [x, y, z] representing the normalized force direction
        """
        return self._impact_force_data.get("final_direction", [0.0, 0.0, 0.0])
    
    @property
    def avg_contact_position(self) -> List[float]:
        """
        Get average position of all contact points.
        
        Returns:
            List [x, y, z] representing average contact position in world coordinates
        """
        return self._impact_force_data.get("avg_contact_position", [0.0, 0.0, 0.0])
    
    @property
    def max_force_sub_object(self) -> str:
        """
        Get name of sub-object experiencing maximum force.
        
        Returns:
            Name of the sub-object (child collider) with the highest impact force
        """
        return self._impact_force_data.get("max_force_sub_object", "")
    
    @property
    def impact_events(self) -> List[str]:
        """
        Get list of current impact event descriptions.
        
        Returns:
            List of strings in format "impactor-->target" describing active collisions
            Example: ["end_effector-->table_surface", "gripper-->cube"]
        """
        return self._impact_force_data.get("impact_events", [])
    
    # ===================  Convenience Methods  ===================
    
    def get_force_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of current force state.
        
        Returns:
            Dictionary containing all force-related data:
            {
                "is_being_hit": bool,
                "total_impact_force": float,
                "total_force_vector": [x, y, z],
                "final_direction": [x, y, z],
                "avg_contact_position": [x, y, z],
                "max_force_sub_object": str,
                "impact_events": [str, ...]
            }
        """
        return {
            "is_being_hit": self.is_being_hit,
            "total_impact_force": self.total_impact_force,
            "total_force_vector": self.total_force_vector,
            "final_direction": self.final_direction,
            "avg_contact_position": self.avg_contact_position,
            "max_force_sub_object": self.max_force_sub_object,
            "impact_events": self.impact_events
        }
    
    def has_force_above(self, threshold: float) -> bool:
        """
        Check if current force exceeds specified threshold.
        
        Args:
            threshold: Force threshold in Newtons
            
        Returns:
            True if total impact force is above threshold, False otherwise
        """
        return self.total_impact_force > threshold
    
    def get_impact_count(self) -> int:
        """
        Get number of active impact events.
        
        Returns:
            Number of simultaneous collisions currently occurring
        """
        return len(self.impact_events)
    
    def clear_force_data(self) -> None:
        """
        Clear locally stored force data.
        
        Note: This only clears local Python data, not Unity's internal state.
        """
        self._impact_force_data = {}