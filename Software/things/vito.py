#!/usr/bin/python3
"""
Created on 29.05.2022

@author: vich
"""
import json
import logging
import time

from .ithing import IThing
from vito_monitor_ctrl import VitocalHandler

log = logging.getLogger("Vito Heatpump")


class Vito(IThing):
    def __init__(self):
        self.vito_handler = VitocalHandler(optolink_settings={}, readout_update=360)

    def get_status(self):
        read_values = self.vito_handler.read_all()
        read_dict = {
            'min_age': float('inf'),
            'max_age': 0
            }
        for elem in read_values:
            read_dict[elem[0]] = elem[1]
            if elem[2]:
                age = time.time() - elem[2]
                if age > read_dict['max_age']:
                    read_dict['max_age'] = age
                if age < read_dict['min_age']:
                    read_dict['min_age'] = age

        read_dict['is_alive'] = self.vito_handler.is_alive()
        if read_dict['max_age'] == 0:
            read_dict['max_age'] = float('inf')
        read_dict['status'] = f"{'OK' if read_dict['is_alive'] else 'ERROR'} age is {read_dict['min_age']:.1f}-{read_dict['max_age']:.1f}s"
        return read_dict

    def set_value(self, channel, value):
        channel_name = channel[0]
        if channel_name == 'configuration':
            try:
                config = json.loads(value)
                self.vito_handler.configure(config)
                return True
            except Exception as e:
                log.error(f"Can't reconfigure, exception {e}. Check the value '{value}'!")
                return False
        else:
            try:
                value_int = int(value.split(' ')[0])
                self.vito_handler.write(channel_name, value_int)
                log.info(f"Set to channel {channel_name} the value {value}.")
                return True
            except Exception as e:
                log.error(f"Can't set to channel {channel_name} the value {value}! Error: {e}")
                return False

    def start(self):
        pass

    def shutdown(self):
        self.vito_handler.stop()


if __name__ == "__main__":
    log_format = '%(asctime)-25s %(name)-25s %(levelname)-10s %(message)s (line %(lineno)d in %(filename)s)'
    logging.basicConfig(format=log_format, level=logging.NOTSET)

    my_vito = Vito()

    while True:
        cmd = input()
        if cmd in ["get", ""]:
            print("State:", my_vito.get_status())
        elif cmd in ["write", "w"]:
            my_vito.set_value("channel", "10")
        elif cmd in ["final", "exit"]:
            my_vito.shutdown()
            break
