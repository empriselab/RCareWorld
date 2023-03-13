from .object import RCareWorldBaseObject
class RCareWorldGameObject(RCareWorldBaseObject):
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

    def copy(self, copy_id: int):
        self.copy_ids.append(copy_id)
        self.env.instance_channel.set_action(
            'Copy',
            id=self.id
        )
        new_object = RCareWorldGameObject(self.env, copy_id, self.object_name + '_copy', is_in_scene=True)
        return new_object

    def translate(self, translation:list):
        """
        Translate a game object by a given distance, in meter format. Note that this command will translate the
       object relative to the current position.
        @param translation:
        @return:
        """
        self.env.instance_channel.set_action(
            'Translate',
            id = self.id,
            translation = translation
        )

    def rotate(self, rotation:list):
        """Rotate a game object by a given rotation, in euler angle format. Note that this command will rotate the
       object relative to the current state. The rotation order will be z axis first, x axis next, and z axis last.
    Args:
        Compulsory:
        index: The index of object, specified in returned message.
        rotation: A 3-d list inferring the relative rotation, in [x,y,z] order.
    """
        self.env.instance_channel.set_action(
            'Rotate',
            id = self.id,
            rotation = rotation
        )

    def setColor(self, color:list):
        self.env.instance_channel.set_action(
            'SetColor',
            id=self.id,
            color=color
        )
