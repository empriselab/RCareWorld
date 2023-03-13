from .object import RCareWorldBaseObject
class RCareWorldRigidObject(RCareWorldBaseObject):
    def __init__(self,
                 env,
                 id:int,
                 name:str,
                 is_in_scene:bool = False):
        super().__init__(
            env=env,
            id=id,
            name=name,
            is_in_scene=is_in_scene
        )

    def getVelocity(self):
        self.env._step()
        vel = self.env.instance_channel.data[self.id]
        return vel

    def getAngularVel(self):
        self.env._step()
        ang_vel = self.env.instance_channel.data[self.id]
        return ang_vel

    def applyConstantForce(self, force:list):
        self.env.instance_channel.set_action(
            'AddForce',
            id = self.id,
            force = force
        )
        self.env._step()

    def setVelocity(self, vel:list):
        self.env.instance_channel.set_action(
            'SetVelocity',
            id = self.id,
            velocity = vel
        )
        self.env._step()

    def GenerateVHACDCollider(self):
        self.env.instance_channel.set_action(
            'GenerateVHACDColider',
            id = self.id
        )
        self.env._step()
