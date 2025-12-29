"""
ArmPoseIoUAttr - Python interface for Unity ArmPoseIoUAttr component

Provides arm pose IoU (Intersection over Union) calculation using capsule-based visualization.
Tracks arm joints and position markers to measure pose similarity.
"""

from typing import List, Dict, Any, Optional
from pyrcareworld.attributes.base_attr import BaseAttr


class FMActionAttr(BaseAttr):
    """
    Foundation model Action Attribute in RCareWorld.
    """

    COMMAND_HEAD = "RandomizeEverything"

    def __init__(self, env, id: int, data: dict = {}):
        """
        Initialize Foundation model Action attribute.
        
        Args:
            env: RCareWorld environment instance
            id: Unique identifier for the GameObject
            data: Optional initialization data dictionary
        """
        super().__init__(env, id, data)
        # Custom initialization if needed
    
    def parse_message(self, data: dict):
        """
        Parse incoming data from Unity FMActionAttr component.
        
        Args:
            data: Dictionary containing IoU measurement data from Unity
        """
        super().parse_message(data)
        
        # Unity can send additional data if needed
        # And in the python script, you can access them via self.data dictionary
    
    def _send_command(self, cmd: str):
        """
        Send a command through the existing RandomizeEverything channel.
        """
        self.env.SendObject(self.COMMAND_HEAD, cmd)

    # ===================  API Methods  ===================
    # Task: Grooming
    def brush(self, affordance: str, distance: float = 0.1):
        """
        Perform a brushing action using the FMActionAttr.
        
        Args:
            affordance: The brushing affordance. List of valid options:
                - "left"
                - "right"
                - "front"
                - "back"
            distance: Distance to brush (default: 0.1)
        """
        # Send command to Unity to perform brushing action with specified parameters
        cmd_map = {
            "left": "brush_left",
            "right": "brush_right",
            "front": "brush_front",
            "back": "brush_back",
        }
        cmd = cmd_map.get(affordance)
        if cmd is None:
            raise ValueError(f"Unknown affordance: {affordance}")
        self._send_command(cmd)

    # Task: Drinking
    
    def drink_acquisition(self, affordance: str, target_position: Optional[List[float]] = None):
        """
        Perform a drinking acquisition action using the FMActionAttr.
        
        Args:
            affordance: The drinking affordance. List of valid options:
                - "Handle"
                - "Cup"
            target_position: Optional target position [x, y, z] for the drinking action
        """
        # Send command to Unity to perform drinking acquisition action with specified parameters
        # if position is none, get the position from unity side
        self._send_command("acquisition")
    
    def move_to_mouth(self, target_position: List[float]):
        """
        Move the drinking object to the mouth position.
        
        Args:
            target_position: Target mouth position [x, y, z]
        """
        # Send command to Unity to move the object to the specified mouth position
        # if position is none, get the position from unity side
        self._send_command("move_to_mouth")
    
    def tilt_cup(self, angle: float):
        """
        Tilt the cup for drinking.
        
        Args:
            angle: Angle in degrees to tilt the cup
        """
        # Send command to Unity to tilt the cup by the specified angle
        # if angle if none, use a default angle
        self._send_command("tilt_cup")
    
    def level_cup(self, angle: float):
        """
        Level the cup back to upright position after drinking.
        """
        # Send command to Unity to level the cup back to upright position
        # if angle if none, use a default angle
        self._send_command("level_cup")
    
    # Task: Feeding
    def open_fridge(self, affordance: str, distance: float = 0.1):
        """
        Open the fridge door using the FMActionAttr.
        
        Args:
            affordance: The fridge door affordance. List of valid options:
                - "LeftDoor"
                - "RightDoor"
                - "Handle"
            distance: Distance to pull back to open the fridge door (default: 0.1)
        """
        # Send command to Unity to open the fridge door with specified parameters
        # if distance is none, use a default distance
        self._send_command("open_fridge")
    
    def pick_plate(self, affordance: str, position: Optional[List[float]] = None):
        """
        Pick up a plate using the FMActionAttr.
        
        Args:
            affordance: The plate affordance. List of valid options:
                - "Plate"
        """
        # Send command to Unity to pick up the plate with specified parameters
        # if position is none, get the position from unity side
        self._send_command("pick_plate")
    
    def close_fridge(self, affordance: str, distance: float = 0.1):
        """
        Close the fridge door using the FMActionAttr.
        
        Args:
            affordance: The fridge door affordance. List of valid options:
                - "LeftDoor"
                - "RightDoor"
                - "Handle"
            distance: Distance to push forward to close the fridge door (default: 0.1)
        """
        # Send command to Unity to close the fridge door with specified parameters
        # if distance is none, use a default distance
        self._send_command("close_fridge")
    
    def pick_utensil(self, affordance: str, position: Optional[List[float]] = None):
        """
        Pick up a utensil using the FMActionAttr.
        
        Args:
            affordance: The utensil affordance. List of valid options:
                - "Fork"
                - "Spoon"
                - "Knife"
            position: Optional target position [x, y, z] for the utensil
        """
        # Send command to Unity to pick up the utensil with specified parameters
        # if position is none, get the position from unity side
        utensil_map = {
            "Fork": "pick_fork",
            "Spoon": None,
            "Knife": None,
        }
        cmd = utensil_map.get(affordance)
        if cmd is None:
            raise ValueError(f"Unsupported utensil affordance: {affordance}")
        self._send_command(cmd)
    
    def move_towards_plate(self, target_position: Optional[List[float]]):
        """
        Move the utensil towards the plate.
        
        Args:
            target_position: Target plate position [x, y, z]
        """
        # Send command to Unity to move the utensil towards the specified plate position
        self._send_command("move_toward_plate")
    
    def bite_acquisition(self, affordance: str, target_position: Optional[List[float]]):
        """
        Perform a bite acquisition action using the FMActionAttr.
        This was called pickup food in the previous version.
        
        Args:
            affordance: The bite affordance. List of valid options:
                - "Food"
            target_position: Target position to acquire the bite 
        """
        # Send command to Unity to perform bite acquisition action with specified parameters
        # if position is none, get the position from unity side
        self._send_command("pick_up_food")
    
    def bite_transfer(self, target_position: Optional[List[float]]):
        """
        Transfer the bite to the mouth position.
        
        Args:
            target_position: Target mouth position [x, y, z]
        """
        # Send command to Unity to transfer the bite to the specified mouth position
        # if position is none, get the position from unity side
        self._send_command("bite_transfer")
    
    def bite_release(self, distance: float = 0.1):
        """
        Release the bite into the mouth.
        """
        # Send command to Unity to release the bite
        # if distance is none, use a default distance, distance means how much to bring in the mouth
        self._send_command("bring_to_mouth")
    
    # Task: Bathing
    def wipe(self, affordance: str, distance: float = 0.1):
        """
        Perform a wiping action using the FMActionAttr.
        
        Args:
            affordance: The wiping affordance. List of valid options:
                - "left_arm"
                - "right_arm"
                - "front"
                - "back"
                - "right leg"
                - "left leg"
            You might want to add more body parts here.
            distance: Distance to wipe (default: 0.1)
        """
        # Send command to Unity to perform wiping action with specified parameters
        cmd_map = {
            "right_arm": "bath_right_arm",
            "right leg": "bath_right_leg",
            "left leg": "bath_left_leg",
            "left_arm": "bath_left_arm",
            "front": "bath_right_arm",
            "back": "bath_left_arm",
        }
        cmd = cmd_map.get(affordance)
        if cmd is None:
            raise ValueError(f"Unknown affordance: {affordance}")
        self._send_command(cmd)
    
    def rinse(self, affordance: str, distance: float = 0.1):
        """
        Perform a rinsing action using the FMActionAttr.
        
        Args:
            affordance: The rinsing affordance. List of valid options:
                - "left_arm"
                - "right_arm"
                - "front"
                - "back"
                - "right leg"
                - "left leg"
            You might want to add more body parts here.
            distance: Distance to rinse (default: 0.1)
        """
        # Send command to Unity to perform rinsing action with specified parameters
        cmd_map = {
            "right_arm": "bath_right_arm",
            "right leg": "bath_right_leg",
            "left leg": "bath_left_leg",
            "left_arm": "bath_left_arm",
            "front": "bath_right_arm",
            "back": "bath_left_arm",
        }
        cmd = cmd_map.get(affordance)
        if cmd is None:
            raise ValueError(f"Unknown affordance: {affordance}")
        self._send_command(cmd)
    
    def dry(self, affordance: str, distance: float = 0.1):
        """
        Perform a drying action using the FMActionAttr.
        
        Args:
            affordance: The drying affordance. List of valid options:
                - "left_arm"
                - "right_arm"
                - "front"
                - "back"
                - "right leg"
                - "left leg"
            You might want to add more body parts here.
            distance: Distance to dry (default: 0.1)
        """
        # Send command to Unity to perform drying action with specified parameters
        # Send command to Unity to perform drying action with specified parameters
        cmd_map = {
            "right_arm": "bath_right_arm",
            "right leg": "bath_right_leg",
            "left leg": "bath_left_leg",
            "left_arm": "bath_left_arm",
            "front": "bath_right_arm",
            "back": "bath_left_arm",
        }
        cmd = cmd_map.get(affordance)
        if cmd is None:
            raise ValueError(f"Unknown affordance: {affordance}")
        self._send_command(cmd)
    
    # Task: Transferring
    def align_lift_to_bed(self, affordance: str, distance: float = 0.1):
        """
        Align and lift the patient to the bed using the FMActionAttr.
        
        Args:
            affordance: The bed affordance. List of valid options:
                - "Bed"
            distance: Distance between bed and lift (default: 0.1)
        """
        # Send command to Unity to align and lift the patient to the bed with specified parameters
        self._send_command("align_lift_to_bed")
    
    def load_patient_on_lift(self):
        """
        Load the patient onto the lift using the FMActionAttr.
        """
        # Send command to Unity to load the patient onto the lift
        self._send_command("load_patient_on_lift")
    
    def raise_lift(self, height: float = 0.5):
        """
        Raise the lift to a specified height using the FMActionAttr.
        
        Args:
            height: Height to raise the lift (default: 0.5)
        """
        # Send command to Unity to raise the lift to the specified height
        self._send_command("raise_patient")
    
    def align_lift_to_destination(self, affordance: str, distance: float = 0.1):
        """
        Align the lift to the destination using the FMActionAttr.
        
        Args:
            affordance: The destination affordance. List of valid options:
                - "Wheelchair"
                - "Bed"
            distance: Distance between lift and destination (default: 0.1)
        """
        # Send command to Unity to align the lift to the destination with specified parameters
        cmd_map = {
            "Wheelchair": "align_lift_to_wheelchair",
            "Bed": "align_lift_to_bed",
        }
        cmd = cmd_map.get(affordance)
        if cmd is None:
            raise ValueError(f"Unknown affordance: {affordance}")
        self._send_command(cmd)
    
    def lower_lift(self, height: float = 0.5):
        """
        Lower the lift to a specified height using the FMActionAttr.
        
        Args:
            height: Height to lower the lift (default: 0.5)
        """
        # Send command to Unity to lower the lift to the specified height
        self._send_command("lower_patient")
    def unload_patient_from_lift(self):
        """
        Unload the patient from the lift using the FMActionAttr.
        """
        # Send command to Unity to unload the patient from the lift
        self._send_command("unload_patient")
    
    def remove_lift(self, affordance: str, distance: float = 0.1):
        """
        Remove the lift from the patient using the FMActionAttr.
        
        Args:
            affordance: The lift affordance. List of valid options:
                - "Lift"
            distance: Distance to move away from the patient (default: 0.1)
        """
        # Send command to Unity to remove the lift from the patient with specified parameters
        self._send_command("remove_lift")
        
    

    # Dressing

    

        
    
    
    
