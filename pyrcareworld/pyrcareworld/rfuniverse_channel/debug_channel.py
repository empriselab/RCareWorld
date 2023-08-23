from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
from pyrcareworld.rfuniverse_channel import RFUniverseChannel


class DebugChannel(RFUniverseChannel):
    """
    Debug utils. Set scripts in Unity.
    """

    def __init__(self, channel_id: str) -> None:
        super().__init__(channel_id)
        self.count = 0
        self.data = {}

    def _parse_message(self, msg: IncomingMessage) -> None:
        return

    def DebugGraspPoint(self, kwargs: dict) -> None:
        """
        Debug the position and rotation of a grasp point.
        See GraspPoint.cs
        @param kwargs:
        @return:
        """
        msg = OutgoingMessage()
        msg.write_string("DebugGraspPoint")
        self.send_message(msg)

    def DebugObjectPose(self, kwargs: dict) -> None:
        """
        Debug object pose. Visualize object global pose with three axis. See PoseGizmo.cs
        @param kwargs:
        @return:
        """
        msg = OutgoingMessage()
        msg.write_string("DebugObjectPose")
        self.send_message(msg)

    def DebugCollisionPair(self, kwargs: dict) -> None:
        """
        Debug collision pair.
        @param kwargs:
        @return:
        """
        msg = OutgoingMessage()
        msg.write_string("DebugCollisionPair")
        self.send_message(msg)

    def DebugColliderBound(self, kwargs: dict) -> None:
        msg = OutgoingMessage()
        msg.write_string("DebugColliderBound")
        self.send_message(msg)

    def DebugObjectID(self, kwargs: dict) -> None:
        msg = OutgoingMessage()
        msg.write_string("DebugObjectID")
        self.send_message(msg)
