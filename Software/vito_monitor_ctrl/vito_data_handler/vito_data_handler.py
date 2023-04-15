"""
Basic Vito Handler
Author: vich-667
"""
import abc
import enum

from vito_monitor_ctrl.optolink_mac import OptolinkMac
from vito_monitor_ctrl.vito_data_handler.config_const import LAST_VALUE, LAST_UPDATE


class InvalidChName(KeyError):
    pass


class UnsupportedWrite(RuntimeError):
    pass


class Mode(enum.IntEnum):
    OffMode = 0
    WarmWater = 1
    HeatAndWarmWater = 2
    UNDEF_3 = 3
    PermanentLow = 4
    PermanentNormal = 5
    NormalOff = 6
    OnlyCooling = 7


class VitoDataHandler(abc.ABC):
    def __init__(self, optolink_mac: OptolinkMac, config: dict):
        self._optolink_mac = optolink_mac
        self._config = config

        # init config with empty data fields
        self.configure(config)

    @staticmethod
    def _decode_data(raw_bytes, unit):
        raw_bytes = raw_bytes[:VitoDataHandler._unit_len(unit)]

        if unit == 'DT':
            # <unit name='DeviceType'>
            #     <abbrev>DT</abbrev>
            #     <type>enum</type>
            #     <enum bytes='20 53 01 2B' text='V200WB2 ID=2053 Protokoll:GWG_VBEM'/>
            # 	  <enum bytes='20 98' text='V200KW2 ID=2098 Protokoll:KW'/>
            # 	  <enum bytes='20 C2' text='VDensHO1 ID=20C2 Protokoll:KW,P300'/>
            #     <enum bytes='20 4D' text='V200-S ID=204D Protokoll:KW,P300'/>
            #     <enum text='UNKNOWN'/>
            # </unit>
            value = raw_bytes
        elif unit == 'UT' or unit == 'UN':
            # < unit name = 'Temperatur' >
            #     <abbrev>UT</abbrev>
            # 	  <calc get='V/10' set='V*10'/>
            # 	  <type>short</type>
            # 	  <entity>Degrees Celsius</entity>
            # </unit>
            # <unit name='Neigung'>
            # 	   <abbrev>UN</abbrev>
            # 	   <calc get='V/10' set='V*10'/>
            # 	   <type>short</type>
            # 	   <entity></entity>
            # 	</unit>
            value = int.from_bytes(raw_bytes, byteorder='little', signed=True)
            value = round(value / 10, 2)
        elif unit == 'CO':
            # <unit name='Counter'>
            # 	  <abbrev>CO</abbrev>
            # 	  <calc get='V' set='V'/>
            # 	  <type>int</type>
            #     <entity></entity>
            # </unit>
            # is currently also used for number without conversion
            value = int.from_bytes(raw_bytes, byteorder='little', signed=True)
        elif unit == 'CS':
            # <unit name='CounterS'>
            #     <abbrev>CS</abbrev>
            #     <calc get='V/3600' set='V*3600'/>
            #     <type>uint</type>
            #     <entity>Stunden</entity>
            # </unit>
            value = int.from_bytes(raw_bytes, byteorder='little', signed=False)
            value = round(value / 3600, 4)
        elif unit == 'RT':
            # <unit name='ReturnStatus'>
            #     <abbrev>RT</abbrev>
            # 	  <type>enum</type>
            # 	  <enum bytes='00' text='0'/>
            # 	  <enum bytes='01' text='1'/>
            # 	  <enum text='NOT OK'/>
            # </unit>
            value = int.from_bytes(raw_bytes, byteorder='little', signed=False)
            if value > 1:
                raise ValueError(f"Type RT is expected with 0 or 1, got {value} from bytes {raw_bytes}")
        elif unit == 'WW':
            # special conversion for 1x Warm Water to allow only to set 0 or 2
            value = int.from_bytes(raw_bytes, byteorder='little', signed=False)
            if value:
                # we always return 1 if != 0
                value = 1
        elif unit == 'BA':
            # <unit name='BetriebsArt'>
            # 	   <abbrev>BA</abbrev>
            # 	   <type>enum</type>
            # 	   <enum bytes='00' text='Abschaltbetrieb'/>
            # 	   <enum bytes='01' text='Warmwasser'/>
            # 	   <enum bytes='02' text='Heizen und Warmwasser'/>
            # 	   <enum bytes='03' text='3'/>
            # 	   <enum bytes='04' text='dauernd reduziert'/>
            # 	   <enum bytes='05' text='dauernd normal'/>
            # 	   <enum bytes='06' text='normal Abschalt'/>
            #  	   <enum bytes='07' text='nur Kuehlen'/>
            # 	   <enum text='UNKNOWN'/>
            # </unit>
            value = int.from_bytes(raw_bytes, byteorder='little', signed=False)
            if value > 7:
                raise ValueError(f"Type BA is enum between 0 and 7, got {value} from bytes {raw_bytes}")
            value = Mode(value).name
        else:
            raise ValueError(f"Can't decode type {unit}")
        return value

    @staticmethod
    def _encode_data(value, unit):
        if unit == 'UT' or unit == 'UN':
            raw_bytes = int.to_bytes(value * 10, length=2, byteorder='little', signed=True)
        elif unit == 'RT':
            raw_bytes = b'\x01' if value else b'\x00'
        elif unit == 'WW':
            # special conversion for 1x Warm Water to allow only to set 0 or 2
            raw_bytes = b'\x02' if value else b'\x00'
        elif unit == 'BA':
            if isinstance(value, str):
                value = int(Mode[value])
            if value > 7:
                raise ValueError(f"Can't encode BA value is above 7: {value}")
            raw_bytes = int.to_bytes(value, length=1, byteorder='little', signed=False)
        elif unit == 'CO':
            raw_bytes = int.to_bytes(value, length=4, byteorder='little', signed=True)
        elif unit == 'CS':
            raw_bytes = int.to_bytes(value * 3600, length=4, byteorder='little', signed=False)
        else:
            raise ValueError(f"Can't encode type {unit}")
        return list(raw_bytes)

    @staticmethod
    def _unit_len(unit):
        if unit == 'RT' or unit == 'WW' or unit == 'BA':
            return 1
        elif unit == 'UT' or unit == 'UN':
            return 2
        elif unit == 'CO' or unit == 'CS':
            return 4
        else:
            raise ValueError(f"Unknown len of type {unit}")

    def configure(self, config: dict):
        # add missing storage values
        for k, v in config.items():
            if LAST_VALUE not in v.keys():
                config[k][LAST_VALUE] = None
            if LAST_UPDATE not in v.keys():
                config[k][LAST_UPDATE] = None
        self._config = config

    @abc.abstractmethod
    def read(self, channel_name: str):
        pass

    @abc.abstractmethod
    def read_all(self):
        pass

    @abc.abstractmethod
    def write(self, channel_name: str, value: int):
        pass

    @abc.abstractmethod
    def stop(self):
        pass
