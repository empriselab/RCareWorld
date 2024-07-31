import pyrcareworld.attributes as attr


class CustomAttr(attr.BaseAttr):
    """
    This is an example of custom attribute class, without actual functions.
    """

    def parse_message(self, data: dict):
        """
        Parse messages. This function is called by internal function.

        Returns:
            Dict: A dict containing useful information of this class.

            data['custom_message']: A custom message
        """
        super().parse_message(data)

    # An example of new API
    def CustomMessage(self, message: str):
        self._send_data("CustomMessage", message)
