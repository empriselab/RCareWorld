from pyrcareworld.envs.base_env import RCareWorld
import pyrcareworld.attributes as attr

class SpongeGrasper(attr.BaseAttr):
    def set_sponge_and_robot(self, sponge_id, sponge_name, robot_id, gripper_name, grasp_radius):
        """
        Set the sponge and robot for the grasper.

        :param sponge_id: ID of the sponge.
        :param sponge_name: Name of the sponge.
        :param robot_id: ID of the robot.
        :param gripper_name: Name of the gripper.
        :param grasp_radius: Radius for grasping.
        """
        self._send_data("SetSpongeAndRobot", sponge_id, sponge_name, robot_id, gripper_name, grasp_radius)

    def is_sponge_being_held(self):
        """
        Check if the sponge is being held.

        :return: Boolean indicating if the sponge is being held.
        """
        self._send_data("IsSpongeBeingHeld")
        self.env._step()
        return self.data.get("IsSpongeBeingHeld")

    def toggle_grasp(self):
        """
        Toggle the grasp state.
        """
        self._send_data("ToggleGrasp")
