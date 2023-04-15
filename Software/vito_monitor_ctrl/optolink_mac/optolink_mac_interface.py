"""
Abstract interface
Author: vich-667
"""
import abc
import enum
import logging
import threading
import time

logger = logging.getLogger("OptolinkMac")


class OptolinkMode(enum.Enum):
    SPY = 0
    READOUT = 1


class OptolinkInvalidMode(RuntimeError):
    pass


class OptolinkCommError(RuntimeError):
    pass


class InterfaceOptolinkMac(abc.ABC, threading.Thread):
    def __init__(self, **kwargs):
        self._mode = OptolinkMode.SPY
        self._rcv_cb = None
        self._data_buffer = bytearray()
        self.buffer_size = 512

        threading.Thread.__init__(self)
        self._poll_data = False

    def run(self) -> None:
        self._poll_data = True
        while self._poll_data:
            try:
                data = self._receive()
            except OptolinkCommError:
                data = None
            if data:
                if self._rcv_cb:
                    try:
                        self._rcv_cb(data)
                    except Exception as e:
                        logger.error(f'Forward data to decoder failed: {e}')
                self._data_buffer += bytearray(data)
                if len(self._data_buffer) > self.buffer_size:
                    self._data_buffer = self._data_buffer[-self.buffer_size:]
                time.sleep(0.01)
            else:
                time.sleep(0.5)

    def set_mode(self, mode: OptolinkMode):
        self._mode = mode

    def get_mode(self) -> OptolinkMode:
        return self._mode

    def register_rcv_cb(self, cb=None):
        self._rcv_cb = cb

    @abc.abstractmethod
    def send(self, data: bytes):
        pass

    @abc.abstractmethod
    def _receive(self) -> bytes:
        return b'data'

    def get_buffer(self) -> bytearray:
        buffer = self._data_buffer
        self._data_buffer = bytearray()
        return buffer

    def close(self):
        self._poll_data = False
        self.join()
