from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

class MovementDetectionAttr(attr.BaseAttr):
    def start_detection(self, detection_time):
        """
        Start the movement detection for the specified time.

        :param detection_time: Time period for detecting the movement.
        """
        self._send_data("StartDetection", float(detection_time))

    def get_movement_results(self):
        """
        Get the results of the movement detection.

        :return: A tuple containing position difference and rotation difference.
        """
        self.env._step()
        position_difference = self.data.get("position_difference", [0, 0, 0])
        rotation_difference = self.data.get("rotation_difference", [0, 0, 0])
        return position_difference, rotation_difference
