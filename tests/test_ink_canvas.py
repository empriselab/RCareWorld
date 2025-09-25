"""
Test InkCanvas functionality

This test demonstrates the InkCanvasAttr Python API and its mapping to C# Unity methods.

===============================================================================
API MAPPING TABLE: InkCanvasAttr
===============================================================================

Python Method                    | C# Unity Method              | Description
---------------------------------|------------------------------|----------------------------------
reset_paint()                    | ResetPaint()                | Reset all painted textures to original
save_painted_textures()          | SavePaintedTextures()       | Save painted textures to PNG files
load_painted_textures()          | LoadPaintedTextures()       | Load painted textures from files
set_save_file_name(str)          | SetSaveFileName(string)     | Set base name for saved files
set_auto_load_on_start(bool)     | SetAutoLoadOnStart(bool)    | Enable/disable auto-load on startup
get_paint_coverage(str)          | GetPaintCoverage(string)    | Get paint coverage % for material

Python Property                  | C# Data                      | Description
---------------------------------|------------------------------|----------------------------------
paint_coverage_percentage        | coverage_percentage (float) | Paint coverage % (0-100)
paint_coverage_material          | material_name (string)      | Material name from last query

===============================================================================
C# Component Hierarchy:
===============================================================================
GameObject with InkCanvasAttr (RCareWorld Attribute)
    └── InkCanvas component (InkPainter plugin)
        └── PaintSet[] (materials with paintable textures)
            ├── Main Texture (color/albedo)
            ├── Normal Map (surface details)
            └── Height Map (parallax)

InkCanvasAttr wraps InkCanvas and exposes [RFUAPI] methods.

===============================================================================
File Persistence:
===============================================================================
Default Save Path: /path/to/project/Assets/.../InkPainter/Script/Core/ink/

File Naming Convention:
- {saveFileName}_main_{index}.png    - Main texture (color)
- {saveFileName}_normal_{index}.png  - Normal map
- {saveFileName}_height_{index}.png  - Height map

Where:
- saveFileName: Set via set_save_file_name()
- index: Material index (0, 1, 2, ...)

===============================================================================
Paint Coverage Calculation:
===============================================================================
Coverage percentage is calculated by:
1. Reading RenderTexture pixels to Texture2D
2. Counting pixels with:
   - Alpha > 0.1 OR
   - RGB values < 0.9 (not white)
3. Percentage = (painted_pixels / total_pixels) * 100

Use cases:
- Washing task: Track how much of body has been washed
- Quality check: Ensure adequate coverage before finishing
- Scoring: Calculate task completion percentage

===============================================================================
Typical Usage Workflow:
===============================================================================
1. Attach InkCanvasAttr to human body GameObject in Unity
2. Configure InkCanvas PaintSet in Unity Inspector:
   - Set main texture property name (e.g., "_MainTex")
   - Enable "Use Main Paint"
   - Optionally enable normal/height painting
3. In Python:
   - Get body attribute and set type to InkCanvasAttr
   - Configure save settings
   - Perform painting via CollisionPainter
   - Query coverage and save results

===============================================================================
Integration with CollisionPainter:
===============================================================================
CollisionPainter → Detects collision → Paints on → InkCanvas

The InkCanvas receives paint commands from CollisionPainter automatically
when the painter's raycasts detect the InkCanvas surface.

===============================================================================
"""

from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr


def test_ink_canvas_api():
    """Test InkCanvas API"""

    ## Initialize environment and get body
    # env = RCareWorld(executable_file="path/to/bathing/scene", graphics=True)
    # body = env.GetAttr(body_id).SetType(attr.InkCanvasAttr)

    ## Configure save settings
    # body.set_save_file_name("bathing_session_001")
    # body.set_auto_load_on_start(False)
    # env.step()

    ## Reset paint
    # body.reset_paint()
    # env.step()

    ## Save painted textures
    # body.save_painted_textures()
    # env.step()

    ## Load painted textures
    # body.load_painted_textures()
    # env.step()

    ## Get paint coverage
    # body.get_paint_coverage("Body_Material")
    # env.step()
    # coverage = body.paint_coverage_percentage
    # material = body.paint_coverage_material

    pass


if __name__ == "__main__":
    ## Initialize environment
    # env = RCareWorld(executable_file="path/to/bathing/scene", graphics=True)

    ## Get body and sponge
    # body_id = 456  # Replace with actual ID
    # sponge_id = 123  # Replace with actual ID
    # body = env.GetAttr(body_id).SetType(attr.InkCanvasAttr)
    # sponge = env.GetAttr(sponge_id).SetType(attr.CollisionPainterAttr)

    ## Setup canvas
    # body.set_save_file_name("bathing_001")
    # body.reset_paint()
    # env.step()

    ## Enable painting
    # sponge.set_can_paint(True)
    # sponge.set_white_mode()
    # env.step()

    ## Check coverage
    # body.get_paint_coverage("Body_Material")
    # env.step()
    # print(f"Coverage: {body.paint_coverage_percentage}%")

    print("InkCanvas test template ready")
    test_ink_canvas_api()