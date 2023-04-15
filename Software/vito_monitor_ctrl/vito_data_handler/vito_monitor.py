"""
Vito Monitor
Author: vich-667
"""
import logging
import time

from vito_monitor_ctrl.optolink_mac import OptolinkMac
from vito_monitor_ctrl.vito_data_handler.config_const import ValueAccess, ADDR, ACCESS, UNIT, LAST_VALUE, LAST_UPDATE
from vito_monitor_ctrl.vito_data_handler.protocol_300 import Protocol300Frame, CorruptedFrame, Prot300MsgType, Prot300ReqType
from vito_monitor_ctrl.vito_data_handler.vito_data_handler import VitoDataHandler, InvalidChName, UnsupportedWrite

logger = logging.getLogger("VitoMonitor")


class VitoMonitor(VitoDataHandler):
    def __init__(self, optolink_mac: OptolinkMac, config: dict):
        super().__init__(optolink_mac=optolink_mac, config=config)

        self.__rcv_buffer = bytearray()

        self._optolink_mac.register_rcv_cb(self.receive_data_cb)

    def receive_data_cb(self, rcv_data):
        self.__rcv_buffer += bytearray(rcv_data)
        self._decode()

    def _decode(self):
        while True:
            # search for next start byte
            index = 0
            try:
                while True:
                    if self.__rcv_buffer[index] == 0x41:
                        # found start byte, drop data before
                        self.__rcv_buffer = self.__rcv_buffer[index:]
                        break
                    else:
                        # increment index
                        index += 1
            except IndexError:
                # no start byte, drop and wait for rcv some data
                self.__rcv_buffer = bytearray()
                return

            # decode the messages
            try:
                frame = Protocol300Frame()
                frame.decode_from_bytes(self.__rcv_buffer)
                self._new_frame_received(frame)
                self.__rcv_buffer = self.__rcv_buffer[frame.length+3:]
            except IndexError:
                # frame is incomplete, lets wait for additional data
                return
            except CorruptedFrame as e:
                logger.debug(f"Corrupt Frame {self.__rcv_buffer[:15]}... , decoding error {e}, skip")
                # Decoding failed skip, goto next
                self.__rcv_buffer = self.__rcv_buffer[1:]

    def _new_frame_received(self, frame: Protocol300Frame):
        if Prot300ReqType(frame.request_type) != Prot300ReqType.VIRTUAL_READ:
            try:
                logger.debug(f"Not a read cmd: {frame}")
            except Exception:
                logger.debug(f"Not a read cmd: {frame.encode_to_bytes()}")
        if Prot300MsgType(frame.message_type) == Prot300MsgType.REQUEST and Prot300ReqType(frame.request_type) == Prot300ReqType.VIRTUAL_READ:
            logger.debug(f"Req data: {frame}")
        if Prot300MsgType(frame.message_type) == Prot300MsgType.RESPONSE and Prot300ReqType(frame.request_type) == Prot300ReqType.VIRTUAL_READ:
            logger.debug(f"Rcv data: {frame}")
            for variable, var_dict in self._config.items():
                if var_dict[ADDR] == frame.address and var_dict[ACCESS] & ValueAccess.MONITOR:
                    try:
                        value = self._decode_data(frame.value, self._config[variable][UNIT])
                        logger.info(f'Found {variable} at {frame.address:02x} with new value {value}')
                        self._config[variable][LAST_VALUE] = value
                        self._config[variable][LAST_UPDATE] = time.time()
                    except Exception as e:
                        logger.error(f'failed to decode {variable}, raised {e}')
                    break

    def read(self, channel_name: str):
        try:
            return self._config[channel_name][LAST_VALUE], self._config[channel_name][LAST_UPDATE]
        except KeyError:
            raise InvalidChName(f"Channel {channel_name} doesn't exist")

    def read_all(self):
        all_vars = []
        for varname, var_dict in self._config.items():
            if var_dict[ACCESS] & ValueAccess.MONITOR:
                all_vars.append([varname, var_dict[LAST_VALUE], var_dict[LAST_UPDATE]])
        return all_vars

    def write(self, channel_name: str, value: int):
        raise UnsupportedWrite('Write not allowed to Monitor')

    def stop(self):
        pass


if __name__ == "__main__":
    log_format = '%(asctime)-25s %(name)-25s %(levelname)-10s %(message)s (line %(lineno)d in %(filename)s)'
    # logging.basicConfig(format=log_format, level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('log.txt')])
    logging.basicConfig(format=log_format, level=logging.INFO)

    # this is basically tested and can be used to analyze further logs
    mac = OptolinkMac(file_name="recordww.txt")     # noqa
    monitor = VitoMonitor(mac, {})

    monitor.configure({})

    # wait for all my data
    input()
    # time.sleep(2)

    data = monitor.read_all()
    print(data)

    from texttable import Texttable
    t = Texttable()
    for i in range(len(data)):
        data[i][2] = time.ctime(data[i][2]) if data[i][2] else None
    data.insert(0, ["Name", "Value", "Time"])
    t.add_rows(data)
    print(t.draw())

    mac.close()
