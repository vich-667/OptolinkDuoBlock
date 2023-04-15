"""
Test Code for Optolink Mac
Author: vich-667
"""
import vito_monitor_ctrl.optolink_mac

if __name__ == "__main__":
    import time

    raw = vito_monitor_ctrl.optolink_mac.OptolinkMac(port='COM4')
    raw.set_mode(vito_monitor_ctrl.optolink_mac.OptolinkMode.READOUT)
    print("SND 'EOT' to reset")
    raw.send(b'\x04')
    time.sleep(3)
    # Periodic 05
    print(f"RCV>>{raw.get_buffer()}<< Wait on 0x05\n")

    print("SND start seq")
    raw.send(b'\x16\x00\x00')
    time.sleep(1)
    # 06 ACK
    print(f"RCV>>{raw.get_buffer()}<< ACK?\n")

    time.sleep(1)
    print("SND req 2 Bytes Address 00 F8")
    # start len req read    address     bytes answ  checksum
    # 41    05  00  01      00 F8       02          00
    raw.send(b'\x41\x05\x00\x01\x00\xF8\x02\x00')
    time.sleep(1)
    # 06 ACK
    # start len resp    read    address     bytes answ  checksum (meine Heizung)
    # 41    07  01      01      00 F8       02    20 4d 70
    print(f"RCV>>{raw.get_buffer()}<< ACK and answer\n")

    time.sleep(1)
    print("SND 'EOT' to reset")
    raw.send(b'\x04')

    print("exit")
    raw.close()
