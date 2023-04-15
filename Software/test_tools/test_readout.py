#!/usr/bin/python3

import serial
import time


class OptolinkMac:
    def __init__(self, **kwargs):
        self.port = 'COM1'
        self.baudrate = 4800
        self.bytesize = 8
        self.parity = serial.PARITY_EVEN
        self.stopbits = serial.STOPBITS_TWO
        self.timeout = 0.250
        self.inter_byte_timeout = 0.100

        self.__dict__.update(kwargs)

        self.serial = None

    def connect(self):
        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=self.timeout,
            inter_byte_timeout=self.inter_byte_timeout
        )

    def send(self, data):
        if not self.serial:
            self.connect()

        self.serial.write(data)  # (snd + '\n').encode('ASCII')
        self.serial.flush()

    def receive(self):
        if not self.serial:
            self.connect()

        return self.serial.read(128)

    def disconnect(self):
        self.serial.close()
        self.serial = None


if __name__ == "__main__":
    raw = OptolinkMac(port='COM5')
    print(f"SND 'EOT' to reset")
    raw.send(b'\x04')
    time.sleep(3)
    print(f"RCV>>{raw.receive()}<<\n")

    print(f"SND start seq")
    raw.send(b'\x16\x00\x00')
    time.sleep(1)
    # 06 ACK
    print(f"RCV>>{raw.receive()}<<\n")

    time.sleep(1)
    print(f"SND req 2 Bytes Addres 00 F8")
    # start len req read    address     bytes answ  checksum
    # 41    05  00  01      00 F8       02          00
    raw.send(b'\x41\x05\x00\x01\x00\xF8\x02\x00')
    time.sleep(1)
    # 06 ACK
    # start len resp    read    address     bytes answ  antwort checksum (meine Heizung)
    # 41    07  01      01      00 F8       02          20 4d   70
    print(f"RCV>>{raw.receive()}<<\n")

    time.sleep(1)
    print(f"SND 'EOT' to reset")
    raw.send(b'\x04')
    raw.disconnect()
