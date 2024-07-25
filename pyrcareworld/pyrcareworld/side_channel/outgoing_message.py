from typing import List
import struct


class OutgoingMessage:
    """
    Utility class for forming the message that is written to a SideChannel.
    All data is written in little-endian format using the struct module.
    """

    def __init__(self):
        """
        Create an OutgoingMessage with an empty buffer.
        """
        self.buffer = bytearray()

    def write_bool(self, b: bool) -> None:
        """
        Append a boolean value.
        """
        self.buffer.extend(int(b).to_bytes(1, byteorder="little"))

    def write_int32(self, i: int) -> None:
        """
        Append an integer value.
        """
        self.buffer.extend(i.to_bytes(4, byteorder="little"))

    def write_float32(self, f: float) -> None:
        """
        Append a float value. It will be truncated to 32-bit precision.
        """
        self.buffer.extend(struct.pack("f", f))

    def write_float32_list(self, float_list: List[float]) -> None:
        """
        Append a list of float values. They will be truncated to 32-bit precision.
        """
        self.write_int32(len(float_list))
        for f in float_list:
            self.write_float32(f)

    def write_string(self, s: str) -> None:
        """
        Append a string value. Internally, it will be encoded to ascii, and the
        encoded length will also be written to the message.
        """
        s_byte = s.encode("utf-8")
        self.write_int32(len(s_byte))
        self.buffer.extend(s_byte)
