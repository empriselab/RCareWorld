from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
from pyrcareworld.rfuniverse_channel import RFUniverseChannel
import pyrcareworld.attributes as attr


class InstanceChannel(RFUniverseChannel):
    def __init__(self, channel_id: str) -> None:
        super().__init__(channel_id)
        self.data = {}

    def _parse_message(self, msg: IncomingMessage) -> None:
        count = msg.read_int32()
        for i in range(count):
            this_object_id = msg.read_int32()
            # print(this_object_id)
            this_object_type = msg.read_string()
            this_object_type = this_object_type.lower()
            # print(this_object_type)
            self.data[this_object_id] = eval(
                "attr." + this_object_type + "_attr." + "parse_message"
            )(msg)

    def set_action(self, action: str, attr_name=None, **kwargs) -> None:
        """Set action and pass corresponding parameters
        Args:
            action: The action name.
            kwargs: keyword argument for action. The parameter list for each action is shown in each function.
        """
        try:
            if attr_name is not None:
                msg = eval("attr." + attr_name + "." + action)(kwargs)
                self.send_message(msg)
            else:
                for i in attr.__all__:
                    if eval("hasattr(attr." + i + ",'" + action + "')"):
                        msg = eval("attr." + i + "." + action)(kwargs)
                        self.send_message(msg)
        except AttributeError:
            print(
                "There is no action called '%s' or this function has a bug, please fix it."
                % action
            )
            exit(-1)
