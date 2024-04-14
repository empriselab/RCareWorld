from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


# Message parsing
def parse_message(msg: IncomingMessage, msg_type: str) -> dict:
    this_data = {}
    # Add your own branch based on the header string
    # CustomMessage corresponds to the first header string in the CustomMessage interface function of Unity's AssetManagerExt script
    if msg_type == "CustomMessage":
        # Read data in order
        #  The reading order corresponds to the writing order before using SendMetaDataToPython in Unity
        data = msg.read_string()
        this_data["custom_message"] = data
    # write data into this_data and return
    return this_data


# Adding new interface example
def CustomMessage(kwargs: dict) -> OutgoingMessage:
    # Mandatory parameters
    compulsory_params = ["message"]
    # Optional parameters
    optional_params = []
    # Parameters check
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()
    # First data to be written must be message type
    # CustomMessage corresponds to the CustomMessage branch of the switch in the AnalysisMsg function of the AssetManagerExt script in Unity
    msg.write_string("CustomMessage")
    # Write the data to be sent in order
    msg.write_string(kwargs["message"])
    return msg
