"""
CollisionPainterAttr - Python interface for Unity CollisionPainter component

Controls texture painting on collision surfaces using raycast detection.
"""

from pyrcareworld.attributes.base_attr import BaseAttr


class CollisionPainterAttr(BaseAttr):
    """
    Collision-based texture painting attribute.

    Example usage:
        sponge = env.GetAttr(sponge_id).SetType(CollisionPainterAttr)
        sponge.set_can_paint(True)
        sponge.set_blue_mode()
        env.step()
    """

    def __init__(self, env, id: int, data: dict = {}):
        super().__init__(env, id, data)

    def parse_message(self, data: dict):
        super().parse_message(data)
        self.data.update(data)

    def set_can_paint(self, can_paint: bool) -> None:
        """
        Enable or disable painting.

        Args:
            can_paint: True to enable painting, False to disable
        """
        self._send_data("SetCanPaint", can_paint)

    def set_paint_mode(self, mode: int) -> None:
        """
        Set paint mode by enum value.

        Args:
            mode: 0=Blue, 1=White, 2=Erase
        """
        self._send_data("SetPaintMode", mode)

    def set_blue_mode(self) -> None:
        """Switch to blue paint mode."""
        self._send_data("SetBlueMode")

    def set_white_mode(self) -> None:
        """Switch to white paint mode."""
        self._send_data("SetWhiteMode")

    def set_erase_mode(self) -> None:
        """Switch to erase mode."""
        self._send_data("SetEraseMode")