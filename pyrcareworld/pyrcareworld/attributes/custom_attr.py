import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


# Message parsing example
def parse_message(msg: IncomingMessage) -> dict:
    # First, read the data inherited from the base class
    this_object_data = attr.base_attr.parse_message(msg)
    # Read data in order
    # The order of reading here corresponds to the writing order in the CollectData function of Unity's CustomAttr script
    this_object_data["custom_message"] = msg.read_string()
    return this_object_data


# New interface example
def CustomMessage(kwargs: dict) -> OutgoingMessage:
    # Mandatory parameters
    compulsory_params = ["id", "message"]
    # Optional parameters
    optional_params = []
    # Parameter check
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()
    # The first data must be ID
    msg.write_int32(kwargs["id"])
    # The second data must be message type. 
    # Here, CustomMessage correspond to one branch of 'switch' in AnalysingMsg function from Unity's new Attr script
    msg.write_string("CustomMessage")
    # Write data in order
    msg.write_string(kwargs["message"])

    return msg