"""
An OMPL plugin for RFUniverse
Modified from pybullet_ompl
To run this demo, you need to install ompl python following its document.

Author: Jieyi Zhang
"""

INTERPOLATE_NUM = 300
DEFAULT_PLANNING_TIME = 500.0

from ompl import base as ob
from ompl import geometric as og
import copy
import pyrcareworld.attributes as attr

class OmplManagerAttr(attr.BaseAttr):
    """
    To use with rfu_OMPL. You need to construct an instance of this class and pass to PbOMPL.
    To run this demo, you need to install ompl python following its document.

    Note:
    This parent class by default assumes that all joints are actuated and should be planned. If this is not your desired
    behavior, please write your own inherited class that overrides respective functionalities.
    """

    def __init__(self, env, id: int, data=None):
        super().__init__(env, id, data)
        self.is_collision = False
        self.state = None
        self.robot_attr = None
        self.joint_num = 0
        self.joint_lower_limit = []
        self.joint_upper_limit = []

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

        :param data: Dictionary containing the message data.
        """
        super().parse_message(data)
        self.is_collision = data["is_collide"]

    def modify_robot(self, robot_id: int):
        """
        Modify the robot's attributes.

        :param robot_id: Int, the ID of the robot.
        """
        self.robot_attr = self.env.GetAttr(robot_id)
        self.joint_num = self.robot_attr.data["number_of_moveable_joints"]
        self.joint_lower_limit = self.robot_attr.data["joint_lower_limit"]
        self.joint_upper_limit = self.robot_attr.data["joint_upper_limit"]

        self._send_data("ModifyRobot", robot_id)

    def get_cur_state(self) -> list:
        """
        Get the current robot state.

        :return: List of current joint values.
        """
        return copy.deepcopy(self.state)

    def set_state(self, state):
        """
        Set the robot state.

        :param state: List of Float, joint values of the robot.
        """
        self.state = state
        self._set_joint_positions(self.state)

    def reset(self):
        """
        Reset the robot state.
        """
        self.state = [0.0] * self.joint_num
        self._set_joint_positions(self.state)

    def _set_joint_positions(self, positions: list):
        """
        Set joint positions.

        :param positions: List of joint positions.
        """
        self.is_collision = False
        self._send_data("SetJointState", positions)

    def RestoreRobot(self, robot_id: int):
        """
        Restore the robot to its initial state.

        :param robot_id: Int, the ID of the robot.
        """
        self._send_data("RestoreRobot", robot_id)

class RFUStateSpace(ob.RealVectorStateSpace):
    """
    Custom state space for RFUniverse.
    """

    def __init__(self, num_dim) -> None:
        super().__init__(num_dim)
        self.num_dim = num_dim
        self.state_sampler = None

    def allocStateSampler(self):
        """
        Allocate a state sampler. This will be called by the internal OMPL planner.
        """
        if self.state_sampler:
            return self.state_sampler
        return self.allocDefaultStateSampler()

    def set_state_sampler(self, state_sampler):
        """
        Set a custom state sampler.

        :param state_sampler: The custom state sampler.
        """
        self.state_sampler = state_sampler

class RFUOMPL:
    """
    RFUniverse OMPL interface for path planning.
    """

    def __init__(self, manager, time_unit=1) -> None:
        """
        Initialize the RFUOMPL class.

        :param manager: An instance of OmplManagerAttr.
        :param time_unit: The time unit for planning.
        """
        self.manager = manager
        self.env = self.manager.env
        self.time_unit = time_unit

        self.space = RFUStateSpace(self.manager.joint_num)

        bounds = ob.RealVectorBounds(self.manager.joint_num)
        upper_bound = self.manager.joint_upper_limit
        lower_bound = self.manager.joint_lower_limit
        for i in range(self.manager.joint_num):
            bounds.setLow(i, lower_bound[i])
            bounds.setHigh(i, upper_bound[i])
        self.space.setBounds(bounds)

        self.ss = og.SimpleSetup(self.space)
        self.ss.setStateValidityChecker(ob.StateValidityCheckerFn(self.is_state_valid))
        self.si = self.ss.getSpaceInformation()

        self.set_planner("InformedRRTstar")

    def is_state_valid(self, state):
        """
        Check if a given state will lead to a collision.

        :param state: The state to check.
        :return: Bool, True if the state is valid, False otherwise.
        """
        self.manager.set_state(self.state_to_list(state))
        self.env.step(2)
        return not self.manager.is_collision

    def set_planner(self, planner_name):
        """
        Set the planner.

        :param planner_name: The name of the planner.
        """
        if planner_name == "PRM":
            self.planner = og.PRM(self.ss.getSpaceInformation())
        elif planner_name == "RRT":
            self.planner = og.RRT(self.ss.getSpaceInformation())
        elif planner_name == "RRTConnect":
            self.planner = og.RRTConnect(self.ss.getSpaceInformation())
        elif planner_name == "RRTstar":
            self.planner = og.RRTstar(self.ss.getSpaceInformation())
        elif planner_name == "EST":
            self.planner = og.EST(self.ss.getSpaceInformation())
        elif planner_name == "FMT":
            self.planner = og.FMT(self.ss.getSpaceInformation())
        elif planner_name == "BITstar":
            self.planner = og.BITstar(self.ss.getSpaceInformation())
        elif planner_name == "InformedRRTstar":
            self.planner = og.InformedRRTstar(self.ss.getSpaceInformation())
        else:
            print(f"{planner_name} not recognized, please add it first")
            return
        self.ss.setPlanner(self.planner)

    def plan_start_goal(self, start, goal, until_success=True, allowed_time=None):
        """
        Plan a path to the goal from the given robot start state.

        :param start: List of start joint positions.
        :param goal: List of goal joint positions.
        :param until_success: Bool, keep planning until success.
        :param allowed_time: Float, allowed planning time.
        :return: Tuple of (Bool, list of states)
        """
        if allowed_time is None:
            allowed_time = self.time_unit

        print("start_planning")
        print(self.planner.params())

        orig_robot_state = self.manager.get_cur_state()

        s = ob.State(self.space)
        g = ob.State(self.space)
        for i in range(len(start)):
            s[i] = start[i]
            g[i] = goal[i]

        self.ss.setStartAndGoalStates(s, g)

        res = False
        self.ss.solve(allowed_time)
        print("Solution Find")
        while True:
            print(f"Found solution: interpolating into {INTERPOLATE_NUM} segments")
            sol_path_geometric = self.ss.getSolutionPath()
            sol_path_geometric.interpolate(INTERPOLATE_NUM)
            sol_path_states = sol_path_geometric.getStates()
            sol_path_list = [self.state_to_list(state) for state in sol_path_states]
            sum_error = sum(abs(goal[i] - sol_path_list[-1][i]) for i in range(self.manager.joint_num))
            if sum_error < 1e-2:
                res = True
            if not until_success or res:
                break
            allowed_time *= 2
            self.ss.solve(allowed_time)

        self.manager.set_state(orig_robot_state)
        self.env.step(50)
        return res, sol_path_list

    def plan(self, goal, allowed_time=DEFAULT_PLANNING_TIME):
        """
        Plan a path to the goal from the current robot state.

        :param goal: List of goal joint positions.
        :param allowed_time: Float, allowed planning time.
        :return: Tuple of (Bool, list of states)
        """
        start = self.manager.get_cur_state()
        return self.plan_start_goal(start, goal, allowed_time=allowed_time)

    def execute(self, path, dynamics=False):
        """
        Execute a planned path and visualize in pybullet.

        :param path: List of states.
        :param dynamics: Bool, allow dynamic simulation. If False, uses robot.set_state() which resets the robot's state without dynamics simulation.
        """
        for q in path:
            if dynamics:
                for i in range(self.manager.num_dim):
                    self.manager.control_attr.SetJointPosition(q)
                    self.env.step(100)
            else:
                self.manager.set_state(q)
            self.env.step()

    def set_state_sampler(self, state_sampler):
        """
        Set a custom state sampler.

        :param state_sampler: The custom state sampler.
        """
        self.space.set_state_sampler(state_sampler)

    def state_to_list(self, state):
        """
        Convert a state to a list.

        :param state: The state to convert.
        :return: List of state values.
        """
        return [state[i] for i in range(self.manager.joint_num)]
