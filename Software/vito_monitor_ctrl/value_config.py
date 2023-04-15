"""
Configuration Data
Author: vich-667
"""
from vito_monitor_ctrl.vito_data_handler import ValueAccess, ADDR, ACCESS, UNIT, DATA_BYTES, DESC

CONFIG = {
    'Aussentemperatur':                 {ADDR: 0x01C1, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,                      DESC: 'Information Allgemein Wertebereich -40 - 70'},
    'VorlauftemperaturSekundaer':       {ADDR: 0x01C5, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,                      DESC: 'Diagnose Anlagenuebersicht Wertebereich 0 - 95'},
    'RuecklauftemperaturSekundaer':     {ADDR: 0x01C6, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,                      DESC: 'Diagnose Anlagenuebersicht Wertebereich 0 - 95'},
    'Warmwassertemperaturoben':         {ADDR: 0x01CD, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,                      DESC: 'Information Warmwasser Wertebereich 0 - 95'},
    'Heizkreispumpe':                   {ADDR: 0x048D, UNIT: 'RT', ACCESS: ValueAccess.MONITOR,                      DESC: 'Information Heizkreis HK1 Wertebereich 0 - 1'},
    'Zirkulationspumpe':                {ADDR: 0x0490, UNIT: 'RT', ACCESS: ValueAccess.MONITOR,                      DESC: 'Information Warmwasser Wertebereich 0 - 1'},
    '3VentilHeizenWW':                  {ADDR: 0x0494, UNIT: 'RT', ACCESS: ValueAccess.MONITOR,                      DESC: 'Diagnose Waermepumpe Wertebereich Heizen:0, WW:1'},
    'Speicherladepumpe':                {ADDR: 0x0496, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,                      DESC: 'Information Warmwasser Wertebereich 0 - 1'},
    'CompressorCycles':                 {ADDR: 0x0500, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,                      DESC: 'Anzahl Einschaltungen Verdichter'},
    'LZCompressor':                     {ADDR: 0x0580, UNIT: 'CS', ACCESS: ValueAccess.MONITOR,                      DESC: 'Laufzeit Compressor in Stunden'},
    'LZHeizstab1':                      {ADDR: 0x0588, UNIT: 'CS', ACCESS: ValueAccess.MONITOR,                      DESC: 'Laufzeit Heizstab Stufe 1 in Stunden'},
    'LZHeizstab2':                      {ADDR: 0x0589, UNIT: 'CS', ACCESS: ValueAccess.MONITOR,                      DESC: 'Laufzeit Heizstab Stufe 2 in Stunden'},
    'LZVerdichterStufe1':               {ADDR: 0x1620, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,                      DESC: 'Laufzeit Verdichter Stufe 1 in Stunden'},
    'LZVerdichterStufe2':               {ADDR: 0x1622, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,                      DESC: 'Laufzeit Verdichter Stufe 2 in Stunden'},
    'LZVerdichterStufe3':               {ADDR: 0x1624, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,                      DESC: 'Laufzeit Verdichter Stufe 3 in Stunden'},
    'LZVerdichterStufe4':               {ADDR: 0x1626, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,                      DESC: 'Laufzeit Verdichter Stufe 4 in Stunden'},
    'LZVerdichterStufe5':               {ADDR: 0x1628, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,                      DESC: 'Laufzeit Verdichter Stufe 5 in Stunden'},
    'Vorlaufsolltemp':                  {ADDR: 0x1800, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,                      DESC: 'Diagnose Heizkreis HK1 Wertebereich 0 - 95'},
    'Raumsolltemp':                     {ADDR: 0x2000, UNIT: 'UT', ACCESS: ValueAccess.MONITOR_WRITE, DATA_BYTES: 3, DESC: 'Bedienung HK1 Wertebereich 10 - 30'},
    'RaumsolltempReduziert':            {ADDR: 0x2001, UNIT: 'UT', ACCESS: ValueAccess.MONITOR_WRITE, DATA_BYTES: 3, DESC: 'Bedienung HK1 Wertebereich 10 - 30'},
    'HeizkennlinieNiveau':              {ADDR: 0x2006, UNIT: 'UN', ACCESS: ValueAccess.MONITOR,                      DESC: 'Bedienung HK1 Wertebereich -15 - 40'},
    'HeizkennlinieNeigung':             {ADDR: 0x2007, UNIT: 'UN', ACCESS: ValueAccess.MONITOR,                      DESC: 'Bedienung HK1 Wertebereich 0 - 3,5'},
    'RaumsolltempParty':                {ADDR: 0x2022, UNIT: 'UT', ACCESS: ValueAccess.MONITOR_WRITE, DATA_BYTES: 3, DESC: 'Bedienung HK1 Wertebereich 10 - 30'},
    'SollLeistungVerdichter':           {ADDR: 0x5030, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,                      DESC: 'Diagnose Anlagenuebersicht Wertebereich 0 - 100'},
    'SolltempWarmwasser':               {ADDR: 0x6000, UNIT: 'UT', ACCESS: ValueAccess.MONITOR_WRITE, DATA_BYTES: 3, DESC: 'Bedienung WW Wertebereich 10 - 60 (95)'},
    'ZweiterSollwert':                  {ADDR: 0x600C, UNIT: 'UT', ACCESS: ValueAccess.MONITOR_WRITE, DATA_BYTES: 3, DESC: 'Bedienung WW Wertebereich 10 - 60 (95)'},
    'Betriebsart':                      {ADDR: 0xB000, UNIT: 'BA', ACCESS: ValueAccess.MONITOR_WRITE, DATA_BYTES: 1, DESC: 'Bedienung HK1 Wertebereich 0 - 4'},
    '1xWWBereitung':                    {ADDR: 0xB020, UNIT: 'WW', ACCESS: ValueAccess.MONITOR_WRITE, DATA_BYTES: 1, DESC: 'Bedienung Normal:0, 1xWW:2'},
    'TempSauggas':                      {ADDR: 0xB409, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,       DATA_BYTES: 3, DESC: 'Temperatur Sauggas [bar] - Kühlmittel'},
    'TempHeissgas':                     {ADDR: 0xB40A, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,       DATA_BYTES: 3, DESC: 'Temperatur Heissgas [bar] - Kühlmittel'},
    'DruckSauggas':                     {ADDR: 0xB410, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,       DATA_BYTES: 3, DESC: 'Druck Sauggas [bar] - Kühlmittel'},
    'DruckHeissgas':                    {ADDR: 0xB411, UNIT: 'UT', ACCESS: ValueAccess.MONITOR,       DATA_BYTES: 3, DESC: 'Druck Heissgas [bar] - Kühlmittel'},
    'VerdichterLeistung':               {ADDR: 0xB423, UNIT: 'CO', ACCESS: ValueAccess.MONITOR,       DATA_BYTES: 4, DESC: 'Verdichter [%] (including one status byte)'},
}
