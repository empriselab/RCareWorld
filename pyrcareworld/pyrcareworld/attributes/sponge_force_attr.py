"""
SpongeForceAttr - Python interface for Unity SpongeForceAttr component

Detects compression force based on mesh intersection volume using sampling.
Calculates force magnitude and normal direction from intersection analysis.
"""

from typing import List, Dict, Any, Optional
from pyrcareworld.attributes.base_attr import BaseAttr


class SpongeForceAttr(BaseAttr):
    """
    Sponge mesh intersection force detection attribute using volume-based calculations.

    Monitors compression forces when the sponge meshes intersect with target object meshes.
    Uses mesh intersection volume multiplied by a force coefficient for realistic force simulation.

    Example usage:
        # Setup - attach to sponge to monitor compression
        sponge = env.GetAttr(sponge_id).SetType(SpongeForceAttr)

        # Configure detection parameters
        sponge.set_volume_force_multiplier(100000.0)  # N/m³
        sponge.set_damping(0.5)
        sponge.set_min_volume_threshold(0.00001)  # 0.01 cm³

        # Set specific target object to detect intersection with
        sponge.set_target_object(human_body_id)

        # Get force data
        sponge.get_sponge_force()
        env.step()

        # Access results
        if sponge.is_intersecting:
            force = sponge.force_magnitude
            direction = sponge.force_normal
            volume = sponge.intersection_volume
    """

    def __init__(self, env, id: int, data: dict = {}):
        """
        Initialize sponge force attribute.

        Args:
            env: RCareWorld environment instance
            id: Unique identifier for the GameObject
            data: Optional initialization data dictionary
        """
        super().__init__(env, id, data)
        self._sponge_force_data: Dict[str, Any] = {}

    def parse_message(self, data: dict):
        """
        Parse incoming data from Unity SpongeForceAttr component.

        Args:
            data: Dictionary containing force measurement data from Unity
        """
        super().parse_message(data)

        # Store sponge force data if received
        if "sponge_force_data" in data:
            self._sponge_force_data = data["sponge_force_data"]

    # ===================  API Methods  ===================

    def get_sponge_force(self) -> None:
        """
        Request current sponge mesh intersection force data from Unity.

        Call env.step() after this method to receive the data.
        Results will be available through property accessors.
        """
        self._send_data("GetSpongeForce")

    def set_volume_force_multiplier(self, multiplier: float) -> None:
        """
        Set volume to force conversion multiplier.

        Controls how intersection volume converts to force magnitude.
        Force = intersection_volume * multiplier

        Args:
            multiplier: Volume force multiplier in N/m³ (minimum 1000.0)
                       Typical values: 10000-1000000 N/m³
        """
        if multiplier < 1000.0:
            multiplier = 1000.0
        self._send_data("SetVolumeForceMultiplier", multiplier)

    def set_damping(self, damping: float) -> None:
        """
        Set damping factor to stabilize force output.

        Controls smoothing of force values to reduce noise and oscillations.

        Args:
            damping: Damping factor between 0.0 and 1.0
                    0.0 = no damping (raw values)
                    1.0 = maximum damping (heavily smoothed)
                    Typical value: 0.5
        """
        if damping < 0.0:
            damping = 0.0
        elif damping > 1.0:
            damping = 1.0
        self._send_data("SetDamping", damping)

    def set_min_volume_threshold(self, threshold: float) -> None:
        """
        Set minimum intersection volume to register force.

        Forces are only calculated when intersection volume exceeds this threshold.
        Helps filter out minor intersections and numerical noise.

        Args:
            threshold: Minimum intersection volume in m³ (minimum 0.0001)
                      Typical values: 0.00001-0.001 m³
        """
        if threshold < 0.0001:
            threshold = 0.0001
        self._send_data("SetMinVolumeThreshold", threshold)

    def set_target_object(self, object_id: int) -> None:
        """
        Set specific target object to detect mesh intersections with.

        When set, forces will only be calculated for mesh intersections with
        the specified object (and its children). Useful for filtering
        specific interactions.

        Args:
            object_id: ID of the target object
                      Use clear_target_object() to disable filtering
        """
        self._send_data("SetTargetObject", object_id)

    def clear_target_object(self) -> None:
        """
        Clear target object to disable mesh intersection filtering.

        After calling this, the sponge will not calculate any forces
        until a new target object is set.
        """
        self._send_data("ClearTargetObject")

    def set_debug_visualization(self, enable: bool) -> None:
        """
        Enable or disable debug visualization in Unity Scene view.

        When enabled, shows force vectors, intersection bounds, and mesh bounds
        as visual gizmos in the Unity editor.

        Args:
            enable: True to enable visualization, False to disable
        """
        self._send_data("SetDebugVisualization", enable)

    def set_enable_realtime_logging(self, enable: bool) -> None:
        """
        Enable or disable Unity real-time console logging.

        Args:
            enable: True to enable real-time logging, False to disable
                   When enabled, Unity will continuously log force data to console
        """
        self._send_data("SetEnableRealtimeLogging", enable)

    def set_log_interval(self, interval: float) -> None:
        """
        Set interval for real-time logging output.

        Controls how frequently the real-time logging outputs data.

        Args:
            interval: Log interval in seconds (0.1 to 2.0)
                     Only affects real-time logging when enabled
        """
        if interval < 0.1:
            interval = 0.1
        elif interval > 2.0:
            interval = 2.0
        self._send_data("SetLogInterval", interval)

    # ===================  Properties  ===================

    @property
    def is_intersecting(self) -> bool:
        """
        Check if sponge meshes are currently intersecting with target meshes.

        Returns:
            True if mesh intersection is detected above threshold, False otherwise
        """
        return self._sponge_force_data.get("is_intersecting", False)

    @property
    def force_magnitude(self) -> float:
        """
        Get magnitude of intersection-based force.

        Calculated as: intersection_volume * volume_force_multiplier
        Value is smoothed by damping factor.

        Returns:
            Force magnitude in Newtons
        """
        return self._sponge_force_data.get("force_magnitude", 0.0)

    @property
    def force_vector(self) -> List[float]:
        """
        Get 3D force vector with direction and magnitude.

        Vector points from intersection center toward sponge center.
        Magnitude represents intersection force strength.

        Returns:
            List [x, y, z] representing force vector in Newtons
        """
        return self._sponge_force_data.get("force_vector", [0.0, 0.0, 0.0])

    @property
    def force_normal(self) -> List[float]:
        """
        Get normalized direction of intersection force.

        Unit vector pointing from intersection center toward sponge center.
        Represents the primary direction of applied force.

        Returns:
            List [x, y, z] representing normalized force direction
        """
        return self._sponge_force_data.get("force_normal", [0.0, 0.0, 0.0])

    @property
    def intersection_volume(self) -> float:
        """
        Get current mesh intersection volume.

        Measures the overlapping volume between sponge and target meshes
        calculated using voxel sampling method.

        Returns:
            Intersection volume in cubic meters (m³)
        """
        return self._sponge_force_data.get("intersection_volume", 0.0)

    @property
    def volume_force_multiplier(self) -> float:
        """
        Get current volume to force conversion multiplier.

        Returns:
            Volume force multiplier in N/m³
        """
        return self._sponge_force_data.get("volume_force_multiplier", 100000.0)

    # ===================  Convenience Methods  ===================

    def get_force_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of current sponge force state.

        Returns:
            Dictionary containing all force-related data:
            {
                "is_intersecting": bool,
                "force_magnitude": float,
                "force_vector": [x, y, z],
                "force_normal": [x, y, z],
                "intersection_volume": float,
                "volume_force_multiplier": float
            }
        """
        return {
            "is_intersecting": self.is_intersecting,
            "force_magnitude": self.force_magnitude,
            "force_vector": self.force_vector,
            "force_normal": self.force_normal,
            "intersection_volume": self.intersection_volume,
            "volume_force_multiplier": self.volume_force_multiplier
        }

    def has_intersection_above(self, threshold: float) -> bool:
        """
        Check if current intersection force exceeds specified threshold.

        Useful for determining if the sponge is being compressed hard enough
        for effective cleaning/bathing actions.

        Args:
            threshold: Force threshold in Newtons

        Returns:
            True if force magnitude is above threshold, False otherwise
        """
        return self.force_magnitude > threshold

    def get_volume_percentage(self, max_volume: float = 0.001) -> float:
        """
        Get intersection volume as percentage of maximum expected volume.

        Useful for visualizing or normalizing intersection amount.

        Args:
            max_volume: Maximum expected intersection volume in m³ (default 0.001m³ = 1cm³)

        Returns:
            Intersection percentage (0.0 to 100.0+)
        """
        if max_volume <= 0:
            return 0.0
        return (self.intersection_volume / max_volume) * 100.0

    def is_in_comfort_range(self, min_force: float = 1.0, max_force: float = 6.0) -> bool:
        """
        Check if force is within comfortable range for bathing.

        Based on typical comfort thresholds for human skin contact.

        Args:
            min_force: Minimum comfortable force in Newtons (default 1.0)
            max_force: Maximum comfortable force in Newtons (default 6.0)

        Returns:
            True if force is within comfort range, False otherwise
        """
        return min_force <= self.force_magnitude <= max_force

    def clear_force_data(self) -> None:
        """
        Clear locally stored force data.

        Note: This only clears local Python data, not Unity's internal state.
        """
        self._sponge_force_data = {}

    def get_force_direction_name(self) -> str:
        """
        Get human-readable description of force direction.

        Returns:
            String describing primary force direction (e.g., "downward", "lateral")
        """
        if not self.is_intersecting:
            return "none"

        normal = self.force_normal
        abs_x, abs_y, abs_z = abs(normal[0]), abs(normal[1]), abs(normal[2])

        # Find dominant axis
        if abs_y > abs_x and abs_y > abs_z:
            return "upward" if normal[1] > 0 else "downward"
        elif abs_x > abs_z:
            return "rightward" if normal[0] > 0 else "leftward"
        else:
            return "forward" if normal[2] > 0 else "backward"

    def get_intersection_info(self) -> Dict[str, Any]:
        """
        Get detailed intersection analysis information.

        Returns:
            Dictionary with intersection analysis data:
            {
                "has_intersection": bool,
                "volume_m3": float,
                "volume_cm3": float,
                "force_per_cm3": float,
                "direction_name": str
            }
        """
        volume_m3 = self.intersection_volume
        volume_cm3 = volume_m3 * 1000000  # Convert m³ to cm³

        force_per_cm3 = 0.0
        if volume_cm3 > 0:
            force_per_cm3 = self.force_magnitude / volume_cm3

        return {
            "has_intersection": self.is_intersecting,
            "volume_m3": volume_m3,
            "volume_cm3": volume_cm3,
            "force_per_cm3": force_per_cm3,
            "direction_name": self.get_force_direction_name()
        }