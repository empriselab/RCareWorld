"""
A OMPL plugin for RFUniverse
Modified from pybullet_ompl

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
    To use with rfu_OMPL. You need to construct a instance of this class and pass to PbOMPL.

    Note:
    This parent class by default assumes that all joints are acutated and should be planned. If this is not your desired
    behaviour, please write your own inheritated class that overrides respective functionalities.

    In addition to the default keys in messages received from Unity
    expected by BaseAttr, the following are expected in this class:

        'is_collide':  Whether there is a collision.
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
        super().parse_message(data)
        self.is_collision = data["is_collide"]

    def modify_robot(self, robot_id: int):
        self.robot_attr = self.env.GetAttr(robot_id)
        self.joint_num = self.robot_attr.data["number_of_moveable_joints"]
        self.joint_lower_limit = self.robot_attr.data["joint_lower_limit"]
        self.joint_upper_limit = self.robot_attr.data["joint_upper_limit"]

        self._send_data("ModifyRobot", robot_id)

    def get_cur_state(self) -> list:
        """
        Get current robot state.
        """
        return copy.deepcopy(self.state)

    def set_state(self, state):
        """
        Set robot state.
        To faciliate collision checking
        Args:
            state: list[Float], joint values of robot
        """
        self.state = state
        self._set_joint_positions(self.state)

    def reset(self):
        """
        Reset robot state
        Args:
            state: list[Float], joint values of robot
        """
        self.state = [0.0] * self.joint_num
        self._set_joint_positions(self.state)

    def _set_joint_positions(self, positions: list):
        self.is_collision = False

        self._send_data("SetJointState", positions)

    def RestoreRobot(self, robot_id: int):
        self._send_data("RestoreRobot", robot_id)


class RFUStateSpace(ob.RealVectorStateSpace):
    def __init__(self, num_dim) -> None:
        super().__init__(num_dim)
        self.num_dim = num_dim
        self.state_sampler = None

    def allocStateSampler(self):
        """
        This will be called by the internal OMPL planner
        """
        # WARN: This will cause problems if the underlying planner is multi-threaded!!!
        if self.state_sampler:
            return self.state_sampler

        # when ompl planner calls this, we will return our sampler
        return self.allocDefaultStateSampler()

    def set_state_sampler(self, state_sampler):
        """
        Optional, Set custom state sampler.
        """
        self.state_sampler = state_sampler


class RFUOMPL:
    def __init__(self, manager, time_unit=1) -> None:
        """
        Args
            robot: A RFUOMPLRobot instance.
            obstacles: list of obstacle ids. Optional.
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
        # self.si.setStateValidityCheckingResolution(0.005)
        # self.collision_fn = pb_utils.get_collision_fn(self.robot_id, self.robot.joint_idx, self.obstacles, [], True, set(),
        #                                                 custom_limits={}, max_distance=0, allow_collision_links=[])

        self.set_planner("InformedRRTstar")  # RRT by default

    def is_state_valid(self, state):
        # check if a given state will lead a collision
        self.manager.set_state(self.state_to_list(state))
        # self.env.SetNextStepNoTimeConsuming()
        self.env.step(2)
        return not self.manager.is_collision

    def set_planner(self, planner_name):
        """
        Note: Add your planner here!!
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
            print("{} not recognized, please add it first".format(planner_name))
            return
        self.ss.setPlanner(self.planner)

    def plan_start_goal(self, start, goal, until_success=True, allowed_time=None):
        """
        plan a path to gaol from the given robot start state
        """
        if allowed_time is None:
            allowed_time = self.time_unit

        print("start_planning")
        print(self.planner.params())

        orig_robot_state = self.manager.get_cur_state()

        # set the start and goal states;
        s = ob.State(self.space)
        g = ob.State(self.space)
        for i in range(len(start)):
            s[i] = start[i]
            g[i] = goal[i]

        # print(self.is_state_valid(goal))
        # print(g)
        # print(goal)
        self.ss.setStartAndGoalStates(s, g)

        # attempt to solve the problem within allowed planning time
        res = False
        self.ss.solve(allowed_time)
        print("Solution Find")
        while True:
            print(
                "Found solution: interpolating into {} segments".format(INTERPOLATE_NUM)
            )
            # print the path to screen
            sol_path_geometric = self.ss.getSolutionPath()
            sol_path_geometric.interpolate(INTERPOLATE_NUM)
            sol_path_states = sol_path_geometric.getStates()
            sol_path_list = [self.state_to_list(state) for state in sol_path_states]
            sum = 0
            last_state = sol_path_list[-1]
            for i in range(self.manager.joint_num):
                sum += abs(goal[i] - last_state[i])
            if sum < 1e-2:
                res = True
            if not until_success or res:
                break
            allowed_time *= 2
            self.ss.solve(allowed_time)

        # reset robot state
        self.manager.set_state(orig_robot_state)
        self.env.step(50)
        return res, sol_path_list

    def plan(self, goal, allowed_time=DEFAULT_PLANNING_TIME):
        """
        plan a path to gaol from current robot state
        """
        start = self.manager.get_cur_state()
        return self.plan_start_goal(start, goal, allowed_time=allowed_time)

    def execute(self, path, dynamics=False):
        """
        Execute a planned plan. Will visualize in pybullet.
        Args:
            path: list[state], a list of state
            dynamics: allow dynamic simulation. If dynamics is false, this API will use robot.set_state(),
                      meaning that the simulator will simply reset robot's state WITHOUT any dynamics simulation. Since the
                      path is collision free, this is somewhat acceptable.
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
        self.space.set_state_sampler(state_sampler)

    def state_to_list(self, state):
        return [state[i] for i in range(self.manager.joint_num)]
