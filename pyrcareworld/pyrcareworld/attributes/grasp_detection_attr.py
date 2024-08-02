import pyrcareworld.attributes as attr

class GraspDetectionAttr(attr.BaseAttr):
    def set_target_and_robot(self, target_id, target_name, robot_id, gripper_name, detection_radius, detection_time, is_cloth):
        """
        Set the target object and robot for the grasp detection.

        :param target_id: ID of the target object.
        :param target_name: Name of the target object.
        :param robot_id: ID of the robot.
        :param gripper_name: Name of the gripper.
        :param detection_radius: Radius for detection.
        :param detection_time: Time for detection.
        :param is_cloth: Boolean indicating if the target is cloth.
        """
        self._send_data("SetTargetAndRobot", target_id, target_name, robot_id, gripper_name, detection_radius, detection_time, is_cloth)

    def start_detection(self):
        """
        Start the grasp detection.
        """
        self._send_data("StartDetection")

    def get_detection_result(self):
        """
        Get the result of the grasp detection.

        :return: Boolean indicating if the grasp was successful.
        """
        self.env._step()
        return self.data.get("is_grasp_successful", False)
