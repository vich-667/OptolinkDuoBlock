"""
Basic Vito Handler
Author: vich-667
"""
import enum


class CorruptedFrame(ValueError):
    pass


class Prot300MsgType(enum.IntEnum):
    REQUEST = 0x00
    RESPONSE = 0x01
    UNACKD = 0x02
    ERROR = 0x03
    UNKNOWN_06 = 0x06
    UNKNOWN_08 = 0x08
    UNKNOWN_09 = 0x09


class Prot300ReqType(enum.IntEnum):
    UNKNOWN_00 = 0x00
    VIRTUAL_READ = 0x01
    VIRTUAL_WRITE = 0x02
    UNKNOWN_03 = 0x03
    UNKNOWN_04 = 0x04
    REMOTE_PROCEDURE_CALL = 0x07
    UNKNOWN_08 = 0x08


class Protocol300Frame:
    def __init__(self):
        self.start_of_frame = None      # Frame starts with 0x41
        self.length = None              # Number of bytes between dem start of frame (0x41) and checksum
        self.message_type = None        # Message identifier lower nibble: 0x00 = Request, 0x01 = Response, 0x02 = UNACKD, 0x03 = Error
        self.request_type = None        # FunctionCode (lower 5 Bits): 0x01 = Virtual_READ, 0x02 = Virtual_WRITE, 0x07 = Remote_Procedure_Call;
        self.sequence_number = None     # FunctionCode (higher Bits 5-7): sequence number
        self.address = None             # 2 Byte value or procedure address
        self.length_value_bytes = None  # bytes to read or write
        self.value = None               # read data or data to write
        self.checksum = None            # checksum
        self.ack = None                 # ack send from vitroninc to the request

    def __str__(self):
        try:
            frame = f"start_of_frame: {self.start_of_frame:02x}; " \
                    f"length: {self.length}; " \
                    f"message_type: {self.message_type:02x}={Prot300MsgType(self.message_type)}; " \
                    f"request_type: {self.request_type:02x}={Prot300ReqType(self.request_type)}; " \
                    f"sequence_number: {self.sequence_number}; " \
                    f"address: {self.address:04x}; " \
                    f"length_value_bytes: {self.length_value_bytes}; " \
                    f"value: {self.value}; " \
                    f"checksum: {self.checksum:02x}; "

            if self.ack:
                frame += f"ack: {self.ack:02x}"
            else:
                frame += "ack: None"
        except TypeError:
            frame = "Not printable frame with undefined values!"

        return frame

    def decode_from_bytes(self, raw_data: bytearray):
        self.start_of_frame = raw_data[0]
        self.length = raw_data[1]                           # Number of bytes between dem start of frame (0x41) and checksum
        frame = raw_data[0:self.length+3]                   # Add start of frame and checksum and length
        if len(frame) != self.length + 3:
            raise IndexError("Framing error, incomplete data")
        if len(frame) < 8:
            raise CorruptedFrame("Seems to have correct length but, missing bytes to decode frame fields")
        self.message_type = frame[2] & 0x0F                 # Message identifier lower nibble: 0x00 = Request, 0x01 = Response, 0x02 = UNACKD, 0x03 = Error
        try:
            Prot300MsgType(self.message_type)
        except ValueError:
            raise CorruptedFrame(f"{self.message_type} is an unknown message type value")
        self.request_type = frame[3] & 0x1F                 # FunctionCode (lower 5 Bits): 0x01 = Virtual_READ, 0x02 = Virtual_WRITE, 0x07 = Remote_Procedure_Call;
        try:
            Prot300ReqType(self.request_type)
        except ValueError:
            raise CorruptedFrame(f"{self.request_type} is an unknown request type value")
        self.sequence_number = (frame[3] & 0xE0) >> 5       # FunctionCode (higher Bits 5-7): sequence number
        self.address = (frame[4] << 8) + frame[5]           # 2 Byte value or procedure address
        self.length_value_bytes = frame[6]                  # bytes to read or write
        self.value = frame[7:-1]                            # read data or data to write

        self.checksum = frame[-1]
        if self.checksum != self._checksum(frame[1:-1]):
            raise CorruptedFrame("Decoding failed because of inconsistent data")

        try:
            if raw_data[self.length+3] != 0x41:               # add next byte as ack if it's not a new start of frame
                self.ack = raw_data[self.length+3]
        except IndexError:
            # It seems, there is no ACK
            pass

        if self.message_type == Prot300MsgType.REQUEST:
            if not self.ack:
                raise CorruptedFrame("Request without an ACK")
            elif self.ack != 0x06:
                raise CorruptedFrame(f"Request without an ACK OK, received {self.ack}")

    @staticmethod
    def _checksum(data):
        checksum = 0
        for a in data:
            checksum += int(a)
            if checksum > 255:
                checksum = checksum - 256
        return checksum

    def read_address(self, address: int, read_len):
        self.start_of_frame = 0x41
        self.length = 0x05
        self.message_type = Prot300MsgType.REQUEST
        self.request_type = Prot300ReqType.VIRTUAL_READ
        self.address = address
        self.length_value_bytes = read_len
        self.checksum = self._checksum([self.length, self.message_type, self.request_type, (self.address & 0xFF00) >> 8, self.address & 0xFF, self.length_value_bytes])

    def write_address(self, address: int, data: list):
        self.start_of_frame = 0x41
        self.length = 0x05 + len(data)
        self.message_type = Prot300MsgType.REQUEST
        self.request_type = Prot300ReqType.VIRTUAL_WRITE
        self.address = address
        self.length_value_bytes = len(data)
        self.value = data
        self.checksum = self._checksum([self.length, self.message_type, self.request_type, (self.address & 0xFF00) >> 8, self.address & 0xFF, self.length_value_bytes] + self.value)

    def encode_to_bytes(self) -> bytes:
        raw = [self.start_of_frame, self.length, self.message_type, self.request_type, (self.address & 0xFF00) >> 8, self.address & 0xFF, self.length_value_bytes]
        if self.value:
            raw += self.value
        raw += [self.checksum]
        return bytes(raw)
