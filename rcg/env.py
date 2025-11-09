import sys
from pathlib import Path
from typing import Optional

# Path Setup - Ensure pyrcareworld is importable
_CURRENT_FILE = Path(__file__).resolve()
_RCG_DIR = _CURRENT_FILE.parent
_PROJECT_ROOT = _RCG_DIR.parent

# Add pyrcareworld to Python path
_PYRCAREWORLD_PATH = _PROJECT_ROOT / "pyrcareworld"
if _PYRCAREWORLD_PATH.exists():
    sys.path.insert(0, str(_PYRCAREWORLD_PATH))
else:
    print(f"[Warning] pyrcareworld not found at {_PYRCAREWORLD_PATH}")

# Import RCareWorld components
from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.controller_attr import ControllerAttr
from pyrcareworld.attributes.camera_attr import CameraAttr
import pyrcareworld.attributes as attr


class KinovaTestEnv(RCareWorld):
    """
    Test environment for Kinova robot with Unity Editor connection.
    
    This environment automatically connects to Unity Editor (no executable needed).
    All object IDs will be configured based on your Unity scene setup.
    """
    
    _kinova_id: int = 315893
    _gripper_id: int = 3158930
    _camera_id: int = 35181

    # Banana objects
    _banana1_id: int = 111111
    _banana2_id: int = 222222
    _banana3_id: int = 333333
    
    def __init__(
        self,
        executable_file: str = "@editor",
        graphics: bool = True,
        port: int = 5004,
        seed: Optional[int] = None,
        *args,
        **kwargs
    ):
        """Initialize Kinova test environment."""
        self.seed = seed
        
        super().__init__(
            executable_file=executable_file,
            graphics=graphics,
            port=port,
            *args,
            **kwargs
        )
        
        # Print connection info
        if executable_file == "@editor":
            print("\n" + "="*70)
            print("[Unity Editor Mode] Kinova Test Environment")
            print("="*70)
            print(f"Waiting for Unity Editor connection on port {port}")
            print(f"Make sure Unity Editor is running and Play mode is active")
            print("="*70 + "\n")
        
        if seed is not None:
            self._apply_seed(seed)
    
    def get_kinova(self) -> ControllerAttr:
        """Get the main Kinova robot controller."""
        try:
            return self.GetAttr(self._kinova_id)
        except AssertionError:
            print(f"Error: Kinova robot with ID {self._kinova_id} not found")
            print(f"Tip: Check Unity Inspector -> RFUniverse Attr -> Instance ID")
            raise
    
    def get_gripper(self) -> ControllerAttr:
        """Get the Kinova gripper controller."""
        try:
            return self.GetAttr(self._gripper_id)
        except AssertionError:
            print(f"Error: Gripper with ID {self._gripper_id} not found")
            raise
    
    def get_camera(self) -> CameraAttr:
        """Get the primary camera for observations."""
        try:
            return self.GetAttr(self._camera_id)
        except AssertionError:
            print(f"Error: Camera with ID {self._camera_id} not found")
            raise

    def get_banana1(self):
        """Get banana1 object."""
        try:
            return self.GetAttr(self._banana1_id)
        except AssertionError:
            print(f"Error: Banana1 with ID {self._banana1_id} not found")
            print(f"Make sure the object exists in Unity with Instance ID = {self._banana1_id}")
            raise

    def get_banana2(self):
        """Get banana2 object."""
        try:
            return self.GetAttr(self._banana2_id)
        except AssertionError:
            print(f"Error: Banana2 with ID {self._banana2_id} not found")
            print(f"Make sure the object exists in Unity with Instance ID = {self._banana2_id}")
            raise

    def get_banana3(self):
        """Get banana3 object."""
        try:
            return self.GetAttr(self._banana3_id)
        except AssertionError:
            print(f"Error: Banana3 with ID {self._banana3_id} not found")
            print(f"Make sure the object exists in Unity with Instance ID = {self._banana3_id}")
            raise


    
    def _apply_seed(self, seed: int):
        """Apply random seed for reproducibility."""
        print(f"Random seed set to: {seed}")
    
    def configure_robot(self,
                       time_step: float = 0.01,
                       joint_stiffness: Optional[list] = None,
                       joint_damping: Optional[list] = None):
        """Configure robot physics parameters."""
        self.SetTimeStep(time_step)
        print(f"Time step set to {time_step}s ({int(1/time_step)}Hz)")
        
        kinova = self.get_kinova()
        
        if joint_stiffness is not None:
            kinova.SetJointStiffness(joint_stiffness)
            print(f"Joint stiffness configured: {joint_stiffness}")
        
        if joint_damping is not None:
            kinova.SetJointDamping(joint_damping)
            print(f"Joint damping configured: {joint_damping}")
        
        self.step()
    
    def reset_robot(self,
                   joint_positions: Optional[list] = None):
        """Reset robot to initial configuration."""
        kinova = self.get_kinova()

        if joint_positions is not None:
            kinova.SetJointPositionDirectly(joint_positions)
            print(f"Robot reset to joint positions: {joint_positions}")
        else:
            print("Warning: No reset configuration provided")

        self.step(50)
    
    def print_scene_info(self):
        """Print information about the current scene configuration."""
        print("\n" + "="*70)
        print("Scene Configuration")
        print("="*70)
        print(f"Kinova Robot ID:     {self._kinova_id}")
        print(f"Gripper ID:          {self._gripper_id}")
        print(f"Camera ID:           {self._camera_id}")
        print(f"Banana1 ID:          {self._banana1_id}")
        print(f"Banana2 ID:          {self._banana2_id}")
        print(f"Banana3 ID:          {self._banana3_id}")
        print("="*70 + "\n")
    
    def test_connection(self):
        """Test connection to Unity and verify basic functionality."""
        try:
            print("Testing Unity connection...")
            self.step(10)
            print("Connection test successful!")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


def create_test_env(
    editor_mode: bool = True,
    graphics: bool = True,
    port: int = 5004,
    **kwargs
) -> KinovaTestEnv:
    """Convenience function to create a test environment."""
    executable = "@editor" if editor_mode else None
    return KinovaTestEnv(
        executable_file=executable,
        graphics=graphics,
        port=port,
        **kwargs
    )


if __name__ == "__main__":
    """Test script - Run this to verify environment setup."""
    print("\nStarting Kinova Test Environment\n")
    
    env = create_test_env(editor_mode=True, graphics=True)
    env.print_scene_info()
    connection_ok = env.test_connection()
    
    if connection_ok:
        print("\nEnvironment ready for testing!")
        print("The environment is now waiting for Unity Editor...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                env.step()
        except KeyboardInterrupt:
            print("\n\nShutting down environment...")
            env.close()
        except Exception as e:
            print(f"\nError during testing: {e}")
            env.close()
    else:
        print("\nEnvironment setup failed!")
        print("Make sure Unity Editor is running and in Play mode")
