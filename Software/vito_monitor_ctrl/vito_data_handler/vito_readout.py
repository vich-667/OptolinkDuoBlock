"""
Vito Readout
Author: vich-667
"""
import enum
import logging
import queue
import threading
import time

from vito_monitor_ctrl.optolink_mac import OptolinkMac, OptolinkMode, OptolinkCommError
from vito_monitor_ctrl.vito_data_handler.protocol_300 import Protocol300Frame, Prot300ReqType, Prot300MsgType
from vito_monitor_ctrl.vito_data_handler.config_const import ValueAccess, ACCESS, ADDR, UNIT, DATA_BYTES, LAST_VALUE, LAST_UPDATE
from vito_monitor_ctrl.vito_data_handler.vito_data_handler import VitoDataHandler, InvalidChName

logger = logging.getLogger("VitoReadout")


class VitoReadoutState(enum.Enum):
    IDLE = 0
    INIT = 1
    READOUT = 2
    TEARDOWN = 3


class VitoReadoutCmd(enum.Enum):
    STOP = 0


class VitoReadout(VitoDataHandler, threading.Thread):
    CON_RETRY = 6

    def __init__(self, optolink_mac: OptolinkMac, config: dict, readout_update: float = 360):
        VitoDataHandler.__init__(self, optolink_mac=optolink_mac, config=config)
        threading.Thread.__init__(self)

        self.readout_update = readout_update
        self._state = VitoReadoutState.IDLE
        self._cmd_queue = queue.Queue()
        self._lock = threading.Lock()
        self.start()

    def run(self) -> None:
        while True:
            if self._state == VitoReadoutState.INIT:
                logger.info('Readout State INIT')
                self._lock.acquire()
                try:
                    sync = self._init_communication()
                except OptolinkCommError as e:
                    logger.error(f"Optolink Communication error on sync up: {e}")
                    sync = None

                # if ok go to readout mode
                if sync:
                    self._state = VitoReadoutState.READOUT
                    logger.debug('Sync Done')
                else:
                    logger.error("Can't sync with Vito control, go back to idle")

                    self._lock.release()
                    self._state = VitoReadoutState.IDLE

            elif self._state == VitoReadoutState.READOUT:
                logger.info('Readout State READOUT')
                # The work need to be done on read and write commands
                for key, var_param in self._config.items():
                    if var_param[ACCESS] & ValueAccess.READOUT:
                        try:
                            logger.debug(f'Readout {key}')
                            value = self._readout(var_param[ADDR], var_param[UNIT], var_param[DATA_BYTES])
                            logger.info(f'Readout {key} returned value {value}')
                            self._config[key][LAST_VALUE] = value
                            self._config[key][LAST_UPDATE] = time.time()
                        except OptolinkCommError as e:
                            logger.error(f"Optolink Communication error on read {key}: {e}")
                            break
                        except Exception as e:
                            logger.warning(f"Read error on var {key}; {e}")
                self._state = VitoReadoutState.TEARDOWN

            elif self._state == VitoReadoutState.TEARDOWN:
                logger.info('Readout State TEARDOWN')
                try:
                    self._teardown_communication()
                except OptolinkCommError as e:
                    logger.error(f"Optolink Communication error on teardown: {e}")
                self._lock.release()
                self._state = VitoReadoutState.IDLE

            else:
                # IDLE we read every n seconds
                logger.info('Readout State IDLE')
                try:
                    cmd = self._cmd_queue.get(True, self.readout_update)
                    if cmd == VitoReadoutCmd.STOP:
                        break   # leave this thread
                except queue.Empty:
                    # check if read is configured, so we go to readout mode
                    for var_param in self._config.values():
                        if var_param[ACCESS] & ValueAccess.READOUT:
                            self._state = VitoReadoutState.INIT
                            break

    def _init_communication(self):
        self._optolink_mac.set_mode(OptolinkMode.READOUT)
        time.sleep(0.7)

        # Do Handshaking
        sync = False
        for i in range(self.CON_RETRY):
            logger.debug('SND EOT to reset')
            self._optolink_mac.get_buffer()  # Clear RCV Buffer
            self._optolink_mac.send(b'\x04')  # SND 'EOT' to reset
            time.sleep(3)   # we need to wait for heater and buffer handling
            rcv_data = self._optolink_mac.get_buffer()
            if rcv_data:
                if rcv_data[-1] == 0x05:  # RCV handshake byte 0x05
                    logger.debug('RCV handshake byte 0x05 OK')
                    self._optolink_mac.send(b'\x16\x00\x00')  # SND Sync seq
                    logger.debug('SND Sync seq 0x16 0x00 0x00')
                    time.sleep(0.7)
                    rcv_data = self._optolink_mac.get_buffer()  # RCV ACK
                    if rcv_data:
                        if rcv_data[-1] == 0x06:
                            logger.debug('RCV ACK 0x06 OK')
                            sync = True
                            break
        if not sync:
            logger.debug('Sync FAILED, SND EOT to reset')
            self._optolink_mac.send(b'\x04')  # SND 'EOT' to reset
            self._optolink_mac.set_mode(OptolinkMode.SPY)
        return sync

    def _teardown_communication(self):
        self._optolink_mac.send(b'\x04')  # SND 'EOT' to reset
        time.sleep(0.7)
        self._optolink_mac.set_mode(OptolinkMode.SPY)

    def _readout(self, address, unit, data_bytes):
        req = Protocol300Frame()
        req.read_address(address, data_bytes)
        self._optolink_mac.send(req.encode_to_bytes())

        start_time = time.time()
        while time.time() < start_time + 5:
            time.sleep(0.7)
            resp_buffer = bytearray(self._optolink_mac.get_buffer())

            # try to decode
            while resp_buffer.find(0x41) != -1:
                resp = Protocol300Frame()
                # Get frame from start
                resp_buffer = resp_buffer[resp_buffer.find(0x41):]
                resp.decode_from_bytes(resp_buffer)
                logger.debug(f'Readout found message {resp}')
                if resp.address == address and resp.message_type == Prot300MsgType.RESPONSE and resp.request_type == Prot300ReqType.VIRTUAL_READ:
                    return self._decode_data(resp.value, unit)
                else:
                    # Shift for next frame
                    resp_buffer = resp_buffer[1:]

        raise IOError('Readout failed')

    def read(self, channel_name: str):
        try:
            return self._config[channel_name][LAST_VALUE], self._config[channel_name][LAST_UPDATE]
        except KeyError:
            raise InvalidChName(f"Channel {channel_name} doesn't exist")

    def read_all(self):
        all_vars = []
        for varname, var_dict in self._config.items():
            if var_dict[ACCESS] & ValueAccess.READOUT:
                all_vars.append([varname, var_dict[LAST_VALUE], var_dict[LAST_UPDATE]])
        return all_vars

    def write(self, channel_name: str, value: int):
        if channel_name in self._config.keys():
            if not self._config[channel_name][ACCESS] & ValueAccess.WRITE:
                raise InvalidChName(f"{channel_name} don't allow write access.")
        else:
            raise InvalidChName(f"Channel name {channel_name} is unknown")

        self._lock.acquire()
        try:
            sync = self._init_communication()

            write_ok = False
            if sync:
                self._optolink_mac.get_buffer()     # clear buffer
                req = Protocol300Frame()
                raw_bytes = self._encode_data(value, self._config[channel_name][UNIT])
                if len(raw_bytes) > self._config[channel_name][DATA_BYTES]:
                    raw_bytes = raw_bytes[:self._config[channel_name][DATA_BYTES]]
                elif len(raw_bytes) < self._config[channel_name][DATA_BYTES]:
                    raw_bytes = raw_bytes + ([0] * (self._config[channel_name][DATA_BYTES] - len(raw_bytes)))
                req.write_address(self._config[channel_name][ADDR], raw_bytes)
                logger.debug(f'Send Write Req {req}')
                self._optolink_mac.send(req.encode_to_bytes())
                time.sleep(1)
                resp = Protocol300Frame()
                resp_buffer = bytearray(self._optolink_mac.get_buffer())
                resp_buffer = resp_buffer[resp_buffer.find(0x41) + 1:]  # remove echo
                resp.decode_from_bytes(resp_buffer[resp_buffer.find(0x41):])
                logger.debug(f'Rcv Write Resp {resp}')
                if resp.message_type == Prot300MsgType.RESPONSE and \
                        resp.request_type == Prot300ReqType.VIRTUAL_WRITE and \
                        resp.address == self._config[channel_name][ADDR]:
                    write_ok = True
                self._teardown_communication()
        except Exception as e:
            self._teardown_communication()
            self._lock.release()
            raise IOError(f'Write of {channel_name} failed with exception: {e}')

        self._lock.release()

        if not sync or not write_ok:
            raise IOError(f'Write of {channel_name} failed: sync {sync}, write {write_ok}')

    def stop(self):
        self._cmd_queue.put(VitoReadoutCmd.STOP)
        self.join()


if __name__ == "__main__":
    log_format = '%(asctime)-25s %(name)-25s %(levelname)-10s %(message)s (line %(lineno)d in %(filename)s)'
    # logging.basicConfig(format=log_format, level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('log.txt')])
    logging.basicConfig(format=log_format, level=logging.DEBUG)

    mac = OptolinkMac(file_name="recordww.txt")     # noqa
    monitor = VitoReadout(optolink_mac=mac, config={}, readout_update=30)

    input("stop\n")

    print(monitor.read_all())

    monitor.stop()
    mac.close()
