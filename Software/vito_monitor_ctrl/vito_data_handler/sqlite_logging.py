"""
Vito Monitor
Author: vich-667
"""
import sqlite3
import time


class LoggingDb:
    def __init__(self, filename="alldata.db"):
        self._con = sqlite3.connect(filename, check_same_thread=False)      # Disable multithreaded check, we crate on init and write in a separate one
        self._cur = self._con.cursor()
        self._cur.execute("CREATE TABLE IF NOT EXISTS value_logging(datetime DATETIME, address INTEGER, raw_data BLOB, var_name TEXT, value REAL)")
        self._con.commit()

    def log(self, datetime, address, raw_data, var_name=None, value=None):
        self._cur.execute("INSERT INTO value_logging VALUES (?, ?, ?, ?, ?)", (datetime, address, raw_data, var_name, value))
        self._con.commit()

    def get_all(self):
        res = self._cur.execute("SELECT datetime, address, raw_data, var_name, value FROM value_logging")
        return res.fetchall()

    def __str__(self):
        return_str = ""
        for row in self._cur.execute("SELECT datetime(datetime, 'unixepoch'), address, raw_data, var_name, value FROM value_logging"):
            return_str += f"{row[0]}, 0x{row[1]:04x}, {row[2]}, {row[3]}, {row[4]}\n"
        return return_str

    def close(self):
        self._con.close()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    import threading
    import time

    db = LoggingDb("test.db")
    db.log(time.time(), 0x0012, b'010203', "bla", 10.0)
    db.log(time.time(), 0x0012, b'010203')
    vales = db.get_all()
    print(vales)

    print("THREAD")

    def logger(db_ref):
        for i in range(2):
            time.sleep(i)
            db_ref.log(time.time(), 0x0010, b'0102AA', "bla", i)

    log_thread = threading.Thread(logger(db))
    log_thread.start()
    log_thread.join()
    print("THREAD DONE")

    print(db)
    # del db
    # print("all done")
