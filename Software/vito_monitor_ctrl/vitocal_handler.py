"""
Vitocal Handler
Author: vich-667
"""
import logging
import threading
import time

from vito_monitor_ctrl.optolink_mac import OptolinkMac, OptolinkMode
from vito_monitor_ctrl.vito_data_handler import VitoMonitor, VitoReadout, InvalidChName, UnsupportedWrite
from vito_monitor_ctrl.value_config import CONFIG


class VitocalHandler:
    """
    Abstract the vito modes by this handler
    """
    def __init__(self, optolink_settings, readout_update=360):
        # factor optolink
        self._optolink = OptolinkMac(**optolink_settings)

        # factor handlers
        self._vito_data_handlers = [VitoMonitor(self._optolink, CONFIG), VitoReadout(self._optolink, CONFIG, readout_update)]

    def read(self, channel_name: str):
        for handler in self._vito_data_handlers:
            value = handler.read(channel_name)
            if value:
                return value
        raise KeyError(f"No variable with key {channel_name} found!")

    def read_all(self):
        values = []
        for handler in self._vito_data_handlers:
            values += handler.read_all()
        return values

    def write(self, channel_name: str, value: int):
        for handler in self._vito_data_handlers:
            try:
                handler.write(channel_name, value)
                return
            except UnsupportedWrite:
                pass
            except Exception as e:
                raise e

        raise InvalidChName(f"No variable with key {channel_name} found!")

    def configure(self, config):
        for handler in self._vito_data_handlers:
            handler.configure(config)

    def is_alive(self):
        alive = self._optolink.is_alive()
        for handler in self._vito_data_handlers:
            if isinstance(handler, threading.Thread):
                alive = alive and handler.is_alive()
        return alive

    def stop(self):
        # Clean up handlers
        for handler in self._vito_data_handlers:
            handler.stop()
        self._vito_data_handlers = None

        # Clean up optolink
        self._optolink.set_mode(OptolinkMode.SPY)
        self._optolink.close()
        self._optolink = None

    def __del__(self):
        if self._vito_data_handlers or self._optolink:
            self.stop()


if __name__ == "__main__":
    log_format = '%(asctime)-25s %(name)-25s %(levelname)-10s %(message)s (line %(lineno)d in %(filename)s)'
    # logging.basicConfig(format=log_format, level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('log.txt')])
    logging.basicConfig(format=log_format, level=logging.DEBUG)

    vito_handler = VitocalHandler(optolink_settings={"file_name": "recordww.txt"}, readout_update=10)

    input("stop\n")
    # time.sleep(2)

    data = vito_handler.read_all()
    print(data)

    from texttable import Texttable
    t = Texttable()
    for i in range(len(data)):
        data[i][2] = time.ctime(data[i][2]) if data[i][2] else None
    data.insert(0, ["Name", "Value", "Time"])
    t.add_rows(data)
    print(t.draw())

    vito_handler.stop()
