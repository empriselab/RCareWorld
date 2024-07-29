import pyrcareworld.attributes as attr


class GraspSimAttr(attr.BaseAttr):
    """
    Grasp pose simulation class.
    
    In addition to the default keys in messages received from Unity
    expected by BaseAttr, the following are expected in this class:

        'done': Whether the simulation is done

        'points': The list of grasp points.

        'quaternions': The list of grasping pose quaternions.

        'width': The list of gripper width of grasping pose.

        'success': The list of success or failure of the grasing pose.
    """

    def StartGraspSim(
        self,
        mesh: str,
        gripper: str,
        points: list,
        normals: list,
        depth_range_min: float,
        depth_range_max: float,
        depth_lerp_count: int,
        angle_lerp_count: int,
        parallel_count: int = 100,
    ):
        """
        Start simulating grasping.

        Args:
            mesh: Str, the absolute path to .obj file.
            gripper: Str, the name of the gripper.
            points: A list of float, representing the grasping points.
            normals: A list of float, representing the normals.
            depth_range_min: Float, the minimum depth of grasp pose.
            depth_range_max: Float, the maximum depth of grasp pose.
            depth_lerp_count: Int, the interpolation count of depth.
            angle_lerp_count: Int, the interpolation count of angle.
            parallel_count: Int, the count of parallel grasping.
        """
        self._send_data(
            "StartGraspSim",
            mesh,
            gripper,
            points,
            normals,
            float(depth_range_min),
            float(depth_range_max),
            depth_lerp_count,
            angle_lerp_count,
            parallel_count,
        )

    def GenerateGraspPose(
        self,
        mesh: str,
        gripper: str,
        points: list,
        normals: list,
        depth_range_min: float,
        depth_range_max: float,
        depth_lerp_count: int,
        angle_lerp_count: int,
    ):
        """
        Generate grasp poses and visualize grasp results.

        Args:
            mesh: Str, the absolute path to .obj file.
            gripper: Str, the name of the gripper.
            points: A list of float, representing the grasping points.
            normals: A list of float, representing the normals.
            depth_range_min: Float, the minimum depth of grasp pose.
            depth_range_max: Float, the maximum depth of grasp pose.
            depth_lerp_count: Int, the interpolation count of depth.
            angle_lerp_count: Int, the interpolation count of angle.
        """
        self._send_data(
            "GenerateGraspPose",
            mesh,
            gripper,
            points,
            normals,
            float(depth_range_min),
            float(depth_range_max),
            depth_lerp_count,
            angle_lerp_count,
        )

    def StartGraspTest(
        self,
        mesh: str,
        gripper: str,
        points: list,
        quaternions: list,
        parallel_count: int = 100,
    ):
        """
        Start testing the grasp based on current grasp poses.

        Args:
            mesh: Str, the absolute path to .obj file.
            gripper: Str, the name of the gripper.
            points: A list of float, representing the grasping points.
            quaternions: A list of float, representing the quaternions.
            parallel_count: Int, the interpolation count of angle.
        """
        self._send_data(
            "StartGraspTest", mesh, gripper, points, quaternions, parallel_count
        )

    def ShowGraspPose(
        self, mesh: str, gripper: str, positions: list, quaternions: list
    ):
        """
        Display grasp poses.

        Args:
            mesh: Str, the absolute path to .obj file.
            gripper: Str, the name of the gripper.
            points: A list of float, representing the grasping points.
            quaternions: A list of float, representing the quaternions.
        """
        self._send_data("ShowGraspPose", mesh, gripper, positions, quaternions)
