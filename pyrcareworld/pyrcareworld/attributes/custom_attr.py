import pyrcareworld.attributes as attr

class CustomAttr(attr.BaseAttr):
    """
    This is an example of a custom attribute class, without actual functions.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

        :param data: Dictionary containing the message data.
        :return: A dict containing useful information of this class.
        :rtype: dict

        data['custom_message']: A custom message.
        """
        super().parse_message(data)

    # An example of a new API
    def CustomMessage(self, message: str):
        """
        Send a custom message.

        :param message: Str, the custom message to be sent.
        """
        self._send_data("CustomMessage", message)
