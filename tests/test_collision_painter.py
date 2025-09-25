"""
Test CollisionPainter functionality

This test demonstrates the CollisionPainterAttr Python API and its mapping to C# Unity methods.

===============================================================================
API MAPPING TABLE: CollisionPainterAttr
===============================================================================

Python Method                    | C# Unity Method              | Description
---------------------------------|------------------------------|----------------------------------
set_can_paint(bool)              | SetCanPaint(bool)           | Enable/disable painting
set_paint_mode(int)              | SetPaintMode(int)           | Set mode: 0=Blue, 1=White, 2=Erase
set_blue_mode()                  | SetBlueMode()               | Switch to blue paint mode
set_white_mode()                 | SetWhiteMode()              | Switch to white paint mode
set_erase_mode()                 | SetEraseMode()              | Switch to erase mode

===============================================================================
C# Component Hierarchy:
===============================================================================
GameObject with CollisionPainterAttr (RCareWorld Attribute)
    └── CollisionPainter component (InkPainter plugin)
        └── Brush component (painting brush settings)

CollisionPainterAttr wraps CollisionPainter and exposes [RFUAPI] methods.

===============================================================================
Paint Mode Enum Values:
===============================================================================
0 = Blue   - Paint with blue color (default: rgba(0, 0.5, 1, 1))
1 = White  - Paint with white color (default: rgba(1, 1, 1, 1))
2 = Erase  - Erase painted areas

===============================================================================
Typical Usage Workflow:
===============================================================================
1. Attach CollisionPainterAttr to sponge GameObject in Unity
2. Attach InkCanvasAttr to human body GameObject in Unity
3. In Python:
   - Get sponge attribute and set type to CollisionPainterAttr
   - Enable painting with set_can_paint(True)
   - Choose paint mode (blue, white, or erase)
   - Move sponge to collide with body surface
   - Raycasts detect collision and paint automatically

===============================================================================
"""

from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr


def test_collision_painter_api():
    """Test CollisionPainter API"""

    ## Initialize environment and get sponge
    # env = RCareWorld(executable_file="path/to/bathing/scene", graphics=True)
    # sponge = env.GetAttr(sponge_id).SetType(attr.CollisionPainterAttr)

    ## Enable painting
    # sponge.set_can_paint(True)
    # env.step()

    ## Switch paint modes
    # sponge.set_blue_mode()      # Blue mode
    # sponge.set_white_mode()     # White mode (soap)
    # sponge.set_erase_mode()     # Erase mode (rinse)
    # env.step()

    ## Set mode directly (0=Blue, 1=White, 2=Erase)
    # sponge.set_paint_mode(0)
    # env.step()

    ## Disable painting
    # sponge.set_can_paint(False)
    # env.step()

    pass


if __name__ == "__main__":
    ## Initialize environment
    # env = RCareWorld(executable_file="path/to/bathing/scene", graphics=True)

    ## Get sponge and set type
    # sponge_id = 123  # Replace with actual ID
    # sponge = env.GetAttr(sponge_id).SetType(attr.CollisionPainterAttr)

    ## Enable painting and set mode
    # sponge.set_can_paint(True)
    # sponge.set_white_mode()  # White soap mode
    # env.step()

    print("CollisionPainter test template ready")
    test_collision_painter_api()