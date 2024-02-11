from .object import RCareWorldBaseObject


class RCareWorldRigidObject(RCareWorldBaseObject):
    def __init__(self, env, id: int, name: str, is_in_scene: bool = False):
        super().__init__(env=env, id=id, name=name, is_in_scene=is_in_scene)

    def getVelocity(self):
        vel = self.env.instance_channel.data[self.id]
        return vel

    def getAngularVel(self):
        ang_vel = self.env.instance_channel.data[self.id]
        return ang_vel

    def applyConstantForce(self, force: list):
        self.env.instance_channel.set_action("AddForce", id=self.id, force=force)

    def setVelocity(self, vel: list):
        self.env.instance_channel.set_action("SetVelocity", id=self.id, velocity=vel)

    def GenerateVHACDCollider(self):
        self.env.instance_channel.set_action("GenerateVHACDColider", id=self.id)
