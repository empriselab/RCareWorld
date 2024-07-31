from typing import List
import struct


class IncomingMessage:
    """
    Utility class for reading the message written to a SideChannel.
    Values must be read in the order they were written.
    """

    def __init__(self, buffer: bytes, offset: int = 0):
        """
        Create a new IncomingMessage from the bytes.
        """
        self.buffer = buffer
        self.offset = offset

    def read_bool(self, default_value: bool = False) -> bool:
        """
        Read a boolean value from the message buffer.
        :param default_value: Default value to use if the end of the message is reached.
        :return: The value read from the message, or the default value if the end was reached.
        """
        if self._at_end_of_buffer():
            return default_value

        self.offset += 1
        return bool(
            int.from_bytes(
                self.buffer[self.offset - 1 : self.offset], byteorder="little"
            )
        )

    def read_int32(self, default_value: int = 0) -> int:
        """
        Read an integer value from the message buffer.
        :param default_value: Default value to use if the end of the message is reached.
        :return: The value read from the message, or the default value if the end was reached.
        """
        if self._at_end_of_buffer():
            return default_value

        self.offset += 4
        return int.from_bytes(
            self.buffer[self.offset - 4 : self.offset], byteorder="little"
        )

    def read_float32(self, default_value: float = 0.0) -> float:
        """
        Read a float value from the message buffer.
        :param default_value: Default value to use if the end of the message is reached.
        :return: The value read from the message, or the default value if the end was reached.
        """
        if self._at_end_of_buffer():
            return default_value

        self.offset += 4
        return struct.unpack("f", self.buffer[self.offset - 4 : self.offset])[0]

    def read_float32_list(self, default_value: List[float] = None) -> List[float]:
        """
        Read a list of float values from the message buffer.
        :param default_value: Default value to use if the end of the message is reached.
        :return: The value read from the message, or the default value if the end was reached.
        """
        if self._at_end_of_buffer():
            return [] if default_value is None else default_value

        list_len = self.read_int32()
        output = []
        for _ in range(list_len):
            output.append(self.read_float32())
        return output

    def read_string(self, default_value: str = "") -> str:
        """
        Read a string value from the message buffer.
        :param default_value: Default value to use if the end of the message is reached.
        :return: The value read from the message, or the default value if the end was reached.
        """
        if self._at_end_of_buffer():
            return default_value

        count = self.read_int32()
        self.offset += count
        return self.buffer[self.offset - count : self.offset].decode("utf-8")

    def _at_end_of_buffer(self) -> bool:
        return self.offset >= len(self.buffer)
