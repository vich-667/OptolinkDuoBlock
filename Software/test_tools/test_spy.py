#!/usr/bin/python3
"""
Python skript to interact with Optolink do IR interface and set the DTR to not disturb the vito.
"""

import os
import serial
import threading


class SerialLogger(threading.Thread):
    def __init__(self, file_name):
        self.run_logger = False
        self.record = False
        self.file_name = os.path.join(os.getcwd(), file_name)
        self.file_name_suffix = ""
        super().__init__()

    def run(self) -> None:
        self.run_logger = True
        while self.run_logger:
            read_data = port_pc.read(128)
            if read_data:
                read_data_str = ""
                for char in read_data:
                    read_data_str += f"{char:02x} "
                read_data_str = read_data_str[:-1]  # remove last blank
                print(f"RCV Pc: {read_data_str}")
                if self.record:
                    with open(file=self.file_name + self.file_name_suffix + ".txt", mode="at") as f:
                        print(read_data_str, file=f)

    def start_rec(self, file_name_suffix: str = ""):
        self.file_name_suffix = file_name_suffix
        self.record = True

    def stop_rec(self):
        self.record = False


"""
Run Test Logger
"""
print(f'Serial Version {serial.VERSION}')

port_pc = serial.Serial(
    # port='/dev/ttyUSB0',
    port='COM4',
    baudrate=4800,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS,
    timeout=0.250,
    inter_byte_timeout=0.100
)

recorder = SerialLogger(file_name="record")
recorder.start()

while True:
    cmd = input(">> ")
    atomCmd = cmd.split(' ')

    if atomCmd[0] == 'exit':
        print('ByeBye')
        break

    elif atomCmd[0] == 'snd':
        snd = atomCmd[1]
        port_pc.write((snd + '\n').encode('ASCII'))
        port_pc.flush()
        print('SND Pc:', (snd + '\n').encode('ASCII'))

    elif atomCmd[0] == 'dtr':
        if atomCmd[1] == 't' or atomCmd[1] == 'True':
            port_pc.dtr = True
            print('DTR Pc True')
        elif atomCmd[1] == 'get':
            print(f'DTR State: {port_pc.dtr}')
        else:
            port_pc.dtr = False
            print('DTR Pc False')
    elif atomCmd[0] == 'rec':
        if atomCmd[1] == 't' or atomCmd[1] == 'True':
            recorder.start_rec(atomCmd[2])
        else:
            recorder.stop_rec()

    else:
        pass

recorder.run_logger = False
port_pc.close()
