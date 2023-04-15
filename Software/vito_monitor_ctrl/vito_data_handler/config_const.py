"""
Configuration Data
Author: vich-667
"""
import enum

ADDR = 'address'
UNIT = 'unit'
ACCESS = 'access'
DESC = 'description'
DATA_BYTES = 'data_bytes'
LAST_VALUE = 'last_value'
LAST_UPDATE = 'last_update'


class ValueAccess(enum.IntEnum):
    MONITOR = 0x01
    READOUT = 0x02
    MONITOR_READOUT = 0x03
    WRITE = 0x04
    MONITOR_WRITE = 0x05
    READOUT_WRITE = 0x06
    ALL = 0x07
