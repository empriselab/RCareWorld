from pyrcareworld.objects.object import RCareWorldBaseObject


class Cloth(RCareWorldBaseObject):
    """
    An Obi Cloth Actor in RCareWorld.
    """

    def __init__(self, env, id: int, name: str, is_in_scene: bool = False):
        super().__init__(env=env, id=id, name=name, is_in_scene=is_in_scene)

    def addParticleAnchor(self, particle_group_name: str, anchor_id: int):
        """
        Add a particle anchor to the cloth actor for the specified particle group and anchored to the object given by anchor_id.
        """
        self.env.instance_channel.set_action(
            "AddParticleAnchor",
            id=self.id,
            particle_group_name=particle_group_name,
            anchor_id=anchor_id,
        )

    def removeParticleAnchor(self, particle_group_name: str):
        """
        Remove a particle anchor from the cloth actor for the specified particle group. Removes ALL anchors for the particle group.
        """
        self.env.instance_channel.set_action(
            "RemoveParticleAnchor",
            id=self.id,
            particle_group_name=particle_group_name,
        )
