import pyrcareworld.attributes as attr

class ClothGrasperAttr(attr.BaseAttr):
    def set_cloth_and_robot(self, cloth_id, cloth_name, robot_id, gripper_name, grasp_radius):
        """
        Set the cloth and robot for the grasper.

        :param cloth_id: ID of the cloth.
        :param cloth_name: Name of the cloth.
        :param robot_id: ID of the robot.
        :param gripper_name: Name of the gripper.
        :param grasp_radius: Radius for grasping particles.
        """
        self._send_data("SetClothAndRobot", cloth_id, cloth_name, robot_id, gripper_name, grasp_radius)

    def is_garment_being_held(self):
        """
        Check if the garment is being held.

        :return: Boolean indicating if the garment is being held.
        """
        self._send_data("IsGarmentBeingHeld")
        self.env._step()
        return self.data.get("is_garment_being_held", False)

    def toggle_grasp_and_gripper(self):
        """
        Toggle the grasp and gripper state.
        """
        self._send_data("ToggleGraspAndGripper")
