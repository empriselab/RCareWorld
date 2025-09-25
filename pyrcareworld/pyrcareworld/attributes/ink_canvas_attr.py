"""
InkCanvasAttr - Python interface for Unity InkCanvas component

Controls texture painting canvas for receiving paint from CollisionPainter.
"""

from pyrcareworld.attributes.base_attr import BaseAttr


class InkCanvasAttr(BaseAttr):
    """
    Texture painting canvas attribute.

    Example usage:
        body = env.GetAttr(body_id).SetType(InkCanvasAttr)
        body.reset_paint()
        env.step()

        # Save painted textures
        body.save_painted_textures()
        env.step()
    """

    def __init__(self, env, id: int, data: dict = {}):
        super().__init__(env, id, data)
        self._paint_coverage_data = {}

    def parse_message(self, data: dict):
        super().parse_message(data)
        self.data.update(data)

        if "paint_coverage_data" in data:
            self._paint_coverage_data = data["paint_coverage_data"]

    def reset_paint(self) -> None:
        """Reset all painted textures to original state."""
        self._send_data("ResetPaint")

    def save_painted_textures(self) -> None:
        """Save all painted textures to files."""
        self._send_data("SavePaintedTextures")

    def load_painted_textures(self) -> None:
        """Load painted textures from saved files."""
        self._send_data("LoadPaintedTextures")

    def set_save_file_name(self, file_name: str) -> None:
        """
        Set the save file name for persistence.

        Args:
            file_name: Base name for saved texture files
        """
        self._send_data("SetSaveFileName", file_name)

    def set_auto_load_on_start(self, auto_load: bool) -> None:
        """
        Enable or disable auto-load on start.

        Args:
            auto_load: True to auto-load saved textures on start
        """
        self._send_data("SetAutoLoadOnStart", auto_load)

    def get_paint_coverage(self, material_name: str) -> None:
        """
        Request paint coverage percentage for a material.
        Call env.step() after this to receive data.

        Args:
            material_name: Name of the material to check
        """
        self._send_data("GetPaintCoverage", material_name)

    @property
    def paint_coverage_percentage(self) -> float:
        """Get paint coverage percentage from last query."""
        return self._paint_coverage_data.get("coverage_percentage", 0.0)

    @property
    def paint_coverage_material(self) -> str:
        """Get material name from last coverage query."""
        return self._paint_coverage_data.get("material_name", "")