import pyrcareworld.attributes as attr

class SoftBodyAttr(attr.BaseAttr):
    """
    Obi Softbody class.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

        :param data: Dictionary containing the message data.
        :return: A dict containing useful information of this class.
        :rtype: dict
        """
        super().parse_message(data)
