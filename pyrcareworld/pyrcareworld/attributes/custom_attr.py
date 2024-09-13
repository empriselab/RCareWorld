import pyrcareworld.attributes as attr

class CustomAttr(attr.BaseAttr):
    """
    This is an example of a custom attribute class, without actual functions.
    
    The data stored in self.data is a dictionary containing the following keys:
        - 'custom_message': a custom message.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by an internal function.

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
