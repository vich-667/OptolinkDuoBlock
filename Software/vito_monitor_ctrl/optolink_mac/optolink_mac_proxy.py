"""
Optolink Mac Proxy
Author: vich-667
"""

# TODO untested

import logging
import serial
import serial.tools.list_ports

from vito_monitor_ctrl.optolink_mac.optolink_mac_interface import InterfaceOptolinkMac, OptolinkMode, OptolinkInvalidMode

logger = logging.getLogger("OptolinkMacSerial")


class OptolinkMacProxy(InterfaceOptolinkMac):
    def __init__(self, **kwargs):

        # set serial line default
        self.port_heater = list(serial.tools.list_ports.comports())[0].device
        self.port_connect = list(serial.tools.list_ports.comports())[1].device
        self.baudrate = 4800
        self.parity = serial.PARITY_EVEN
        self.stopbits = serial.STOPBITS_TWO
        self.bytesize = serial.EIGHTBITS
        self.timeout = 0.250
        self.inter_byte_timeout = 0.100
        # override with kwargs
        self.__dict__.update(kwargs)
        # init serial line
        self.__serial_heater = serial.Serial(
            port=self.port_heater,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=self.timeout,
            inter_byte_timeout=self.inter_byte_timeout
        )
        self.__serial_connect = serial.Serial(
            port=self.port_connect,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=self.timeout,
            inter_byte_timeout=self.inter_byte_timeout
        )
        logger.debug(f'Serial init heater {self.__serial_heater}, connect {self.__serial_connect}')

        # start super class thread
        super().__init__(**kwargs)
        self.start()

        # initialize mode, set serial line
        self.set_mode(self._mode)

    def send(self, data: bytes):
        if self._mode == OptolinkMode.READOUT:
            self.__serial_heater.write(data)
            self.__serial_heater.flush()
            logger.debug(f'Serial send heater {data}')
        else:
            raise OptolinkInvalidMode('Readout mode must be set before sending')

    def _receive(self):
        readout_heater = self.__serial_heater.read(128)
        if readout_heater:
            logger.debug(f'Serial read heater {readout_heater}')
            if self.set_mode == OptolinkMode.SPY:
                self.__serial_connect.write(readout_heater)

        readout_connect = self.__serial_connect.read(128)
        if readout_connect and self._mode == OptolinkMode.SPY:
            logger.debug(f'Serial read connect {readout_connect}')
            self.__serial_heater.write(readout_connect)

        return bytes(bytearray(readout_connect) + bytearray(readout_heater))    # TODO this might not work, we need to make sure the half duplex framing here

    def close(self):
        super().close()
        self.__serial_heater.close()
        self.__serial_connect.close()
        self.__serial_heater = None
        self.__serial_connect = None
