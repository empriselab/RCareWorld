import pyrcareworld.attributes as attr


class CustomAttr(attr.BaseAttr):
    """
    This is an example of custom attribute class, without actual functions.
    """

    # An example of new API
    def CustomMessage(self, message: str):
        self._send_data("CustomMessage", message)
