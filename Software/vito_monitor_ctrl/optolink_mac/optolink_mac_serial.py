"""
Optolink Mac for serial line
Author: vich-667
"""
import logging
import time

import serial
import serial.tools.list_ports

from vito_monitor_ctrl.optolink_mac.optolink_mac_interface import InterfaceOptolinkMac, OptolinkMode, OptolinkInvalidMode, OptolinkCommError

logger = logging.getLogger("OptolinkMacSerial")


class OptolinkMacSerial(InterfaceOptolinkMac):
    def __init__(self, **kwargs):
        # set serial line default
        self.port = list(serial.tools.list_ports.comports())[0].device
        self.baudrate = 4800
        self.parity = serial.PARITY_EVEN
        self.stopbits = serial.STOPBITS_TWO
        self.bytesize = serial.EIGHTBITS
        self.timeout = 0.250
        self.inter_byte_timeout = 0.100
        # override with kwargs
        self.__dict__.update(kwargs)
        # init super class
        super().__init__(**kwargs)

        # open serial port
        self.__serial = None
        self.__open_port()

        # start super class thread
        self.start()

    def __open_port(self):
        if self.__serial:
            try:
                self.__serial.close()
            except Exception as e:
                logger.error(f'Close port before init serial port error: {e}')
            self.__serial = None
            time.sleep(1)

        # init serial line
        try:
            self.__serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=self.parity,
                stopbits=self.stopbits,
                bytesize=self.bytesize,
                timeout=self.timeout,
                inter_byte_timeout=self.inter_byte_timeout
            )
            # initialize mode, set serial line
            self.__set_mode_serial()
            logger.info(f'Init serial port {self.__serial}')
        except Exception as e:
            logger.error(f'Init serial port error: {e}')
            self.__serial = None
            raise OptolinkCommError(f'Failed to open serial port. {e}')

    def __set_mode_serial(self):
        if self._mode == OptolinkMode.READOUT:
            self.__serial.dtr = False
            logger.debug('Serial set mode dtr False')
        else:
            # Spy Mode default
            self.__serial.dtr = True
            logger.debug('Serial set mode dtr True')

    def set_mode(self, mode: OptolinkMode):
        super().set_mode(mode)
        try:
            self.__set_mode_serial()
            logger.debug(f'Serial set mode {mode}')
        except Exception as e:
            logger.error(f'Serial set mode error: {e}')
            try:
                self.__open_port()      # includes call to __set_mode_serial()
                logger.debug(f'Serial set mode {mode}')
            except Exception as e:
                raise OptolinkCommError(f'Failed to set mode of serial port. {e}')

    def send(self, data: bytes):
        if self._mode == OptolinkMode.READOUT:
            try:
                self.__serial.write(data)
                self.__serial.flush()
                logger.debug(f'Serial send {data}')
            except Exception as e:
                logger.error(f'Serial set mode error: {e}')
                try:
                    self.__open_port()
                    self.__serial.write(data)
                    self.__serial.flush()
                    logger.debug(f'Serial send {data}')
                except Exception as e:
                    raise OptolinkCommError(f'Failed to send on serial port. {e}')
        else:
            raise OptolinkInvalidMode('Readout mode must be set before sending.')

    def _receive(self):
        try:
            readout = self.__serial.read(128)
            if readout:
                logger.debug(f'Serial read {readout}')
            return readout
        except Exception as e:
            logger.error(f'Serial read error: {e}')
            self.__open_port()
            raise OptolinkCommError('Read from serial port.')

    def close(self):
        super().close()
        try:
            self.__serial.close()
        except Exception:
            pass
        self.__serial = None
