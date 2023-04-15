#!/usr/bin/python3
"""
Vito Monitor Ctrl Main Application
Author: vich-667
"""
import logging
import sys
import texttable
import time
import traceback

from vito_monitor_ctrl import VitocalHandler


def main(debug=""):
    log_format = '%(asctime)-25s %(name)-25s %(levelname)-10s %(message)s (line %(lineno)d in %(filename)s)'
    if debug and debug != "log":
        logging.basicConfig(format=log_format, level=logging.DEBUG)
    elif debug == "log":
        logging.basicConfig(format=log_format, level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('log.txt')])
    else:
        logging.basicConfig(format=log_format, level=logging.WARNING)

    vito_handler = VitocalHandler(optolink_settings={"file_name": "recordboot.txt"}, readout_update=30)

    while True:
        print("Enter cmd")
        cmd = input()
        if cmd in ["exit", "stop", "kill"]:
            print("bye bye")
            break
        elif cmd.startswith("w "):
            atom_cmd = cmd.split(" ")
            try:
                vito_handler.write(atom_cmd[1], int(atom_cmd[2]))
            except Exception as e:
                print(f"Exception {e}")
                traceback.print_exc()
        elif cmd:
            try:
                value = vito_handler.read(cmd)
                print(f"Read {cmd}: {value}")
            except Exception as e:
                print(f"Read {cmd} failed with error: {e}")
        else:
            data = vito_handler.read_all()
            # print(data)
            for i in range(len(data)):
                data[i][2] = time.ctime(data[i][2]) if data[i][2] else None
            data.insert(0, ["Name", "Value", "Time"])
            t = texttable.Texttable()
            t.add_rows(data)
            print(t.draw())
            if debug == "log":
                f = open("data.table", "w")
                f.write(t.draw())
                f.close()

    vito_handler.stop()


if __name__ == "__main__":
    main("debug")
