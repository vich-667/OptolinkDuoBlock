"""
Dummy implementation for debugging
Author: vich-667
"""
import logging
import os

from vito_monitor_ctrl.optolink_mac.optolink_mac_interface import InterfaceOptolinkMac, OptolinkMode, OptolinkInvalidMode

logger = logging.getLogger("OptolinkMacDummy")


class OptolinkMacDummy(InterfaceOptolinkMac):
    def __init__(self, **kwargs):
        # get dummy data
        self.__data_records = []
        self.__idx = 0
        if 'file_name' in kwargs:
            file_name = kwargs['file_name']
        else:
            file_name = "recordboot.txt"
        filename = os.path.join(os.path.join(os.path.split(os.getcwd())[0], "log_data"), file_name)
        with open(filename, "rt") as f:
            for line in f.readlines():
                self.__data_records.append(bytes.fromhex(line.strip()))
        logger.debug('Dummy init')

        # start super class thread
        super().__init__(**kwargs)
        self.start()

    def set_mode(self, mode: OptolinkMode):
        super().set_mode(mode)
        logger.debug(f'Dummy set mode {self._mode}')

    def send(self, data: bytes):
        if self._mode == OptolinkMode.READOUT:
            logger.debug(f'Dummy send {data}')
        else:
            raise OptolinkInvalidMode('Readout mode must be set before sending')

    def _receive(self):
        try:
            readout = self.__data_records[self.__idx]
            self.__idx += 1
        except IndexError:
            # readout = self.__data_records[0]
            readout = bytearray()
            # self.__idx = 1
        logger.debug(f'Dummy read {readout}')
        return readout
