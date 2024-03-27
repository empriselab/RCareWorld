import numpy as np

class Control:
    def __init__(self, robot):
        self.robot = robot
        self.ik_controller = robot.ik_controller

    def osc_ee_control(self, currentJointPos, currentJointVel, desPos, desVel, Kp, Kd):
            def unity_pos_to_bullet_pos(pos: list):
                return np.array([pos[2], -pos[0], pos[1]])

            currState = self.getRobotState()
            currentEEPos = currState['positions'][-1]
            currentEEVel = currState["velocities"][-3]
            
            currentEEPos = unity_pos_to_bullet_pos(currentEEPos)
            currentEEVel = unity_pos_to_bullet_pos(currentEEVel)
            desPos = unity_pos_to_bullet_pos(desPos)
            desVel = unity_pos_to_bullet_pos(desVel)
            
            des_x_dd = Kp*(desPos - currentEEPos) + Kd*(desVel - currentEEVel)
            
            # # assume end effector link num = 8
            Jee, Jr= self.ik_controller.calc_jacobian(7, [0, 0, 0], currentJointPos, currentJointVel, [0, 0, 0, 0, 0, 0, 0])

            Mq = self.ik_controller.calc_Mq(currentJointPos)
            
            # gq = self.ik_controller.calc_gq(currentPos, currentVel, [0, 0, 0, 0, 0, 0 , 0])
            Jee_T = np.transpose(Jee)
            
            Mxee = np.linalg.inv(np.matmul(Jee, np.matmul(np.linalg.inv(Mq), Jee_T)))
            
            
            internal = np.transpose(np.matmul(Mxee, des_x_dd))
            
            # u = np.transpose(gq)
            u = np.matmul(Jee_T, internal) # + np.transpose(gq)

            #return u
            return u #jointVels, jointVelocities, diff #, com

