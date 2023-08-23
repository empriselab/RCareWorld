from pyrcareworld.side_channel import SideChannel
from pyrcareworld.side_channel import IncomingMessage
from pyrcareworld.side_channel import OutgoingMessage
import uuid
from abc import abstractmethod
from typing import Union


class RFUniverseChannel(SideChannel):
    def __init__(self, channel_id: Union[uuid.UUID, str]) -> None:
        if type(channel_id) is str:
            super().__init__(uuid.UUID(channel_id))
        else:
            super().__init__(channel_id)

    def on_message_received(self, msg: IncomingMessage) -> None:
        self._parse_message(msg)

    def send_message(self, msg: OutgoingMessage) -> None:
        super().queue_message_to_send(msg)

    def vis_data(self, data: dict):
        for idx in data.keys():
            for key in data[idx].keys():
                print(key, data[idx][key])
            print("")

    @abstractmethod
    def _parse_message(self, msg: IncomingMessage) -> None:
        """Parse incoming message. This is an abstract method, implemented in each channel.
        Args:
            msg: IncomingMessage, the incoming message
        """
        raise NotImplementedError("Please implement _parse_message method.")

    def _check_kwargs(self, kwargs: dict, compulsory_params: list):
        """Check keyword arguments, make sure all compulsory parameters are included.
        Args:
            kwargs: Keyword arguments.
            compulsory_params: Compulsory parameters.
        """
        legal = True
        for param in compulsory_params:
            if param not in kwargs.keys():
                legal = False
                assert legal, "Parameters illegal, parameter <%s> missing." % param

    def set_action(self, action: str, **kwargs) -> None:
        """Set action and pass corresponding parameters
        Args:
            action: The action name.
            kwargs: keyword argument for action. The parameter list for each action is shown in each function.
        """
        try:
            eval("self." + action)(kwargs)
        except AttributeError:
            print(
                "There is no action called '%s' or this function has bug, please fix it."
                % action
            )
            exit(-1)
