"""
Test code to basically test the optolink duo block with an IR test Prove and both interfaces
"""

import serial

print(f'Serial Version {serial.VERSION}')

portPc = serial.Serial(
    port='COM7',
    baudrate=4800,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS,
    timeout=0.250,
    inter_byte_timeout=0.100
)

portVito = serial.Serial(
    port='COM5',
    baudrate=4800,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS,
    timeout=0.250,
    inter_byte_timeout=0.100
)

portTest = serial.Serial(
    port='COM9',
    baudrate=4800,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS,
    timeout=0.250,
    inter_byte_timeout=0.100
)

while True:
    cmd = input(">> ")
    atomCmd = cmd.split(' ')

    if atomCmd[0] == 'exit':
        print('ByeBye')
        break

    elif atomCmd[0] == 'pc':
        snd = atomCmd[1]
        portPc.write((snd + '\n').encode('ASCII'))
        portPc.flush()
        print('SND Pc:', (snd + '\n').encode('ASCII'))

    elif atomCmd[0] == 'vito':
        snd = atomCmd[1]
        portVito.write((snd + '\n').encode('ASCII'))
        portVito.flush()
        print('SND Vito:', (snd + '\n').encode('ASCII'))

    elif atomCmd[0] == 'test':
        snd = atomCmd[1]
        portTest.write((snd + '\n').encode('ASCII'))
        portTest.flush()
        print('SND Test:', (snd + '\n').encode('ASCII'))

    elif atomCmd[0] == 'dtr':
        if atomCmd[1] == 't' or atomCmd[1] == 'True':
            portPc.dtr = True
            print('DTR Pc True')
        else:
            portPc.dtr = False
            print('DTR Pc False')
    else:
        pass

    invaluePc = portPc.read(128)
    if invaluePc:
        print('RCV Pc:', invaluePc)
    try:
        invalueVito = portVito.read(128)
        if invalueVito:
            print('RCV Vito:', invalueVito)
    except Exception as e:
        print(e)
        pass

    invalueTest = portTest.read(128)
    if invalueTest:
        print('RCV Test:', invalueTest)

portPc.close()
portVito.close()
portTest.close()
