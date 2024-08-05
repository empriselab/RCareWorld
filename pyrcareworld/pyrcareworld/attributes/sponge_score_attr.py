import pyrcareworld.attributes as attr

class SpongeScoreAttr(attr.BaseAttr):
    """
    Sponge score attribute class to interact with the sponge score in the Unity environment.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

        :param data: Dictionary containing the message data.
        :return: A dict containing useful information of this class.
        :rtype: dict
        """
        super().parse_message(data)
