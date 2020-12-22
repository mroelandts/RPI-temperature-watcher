#!/usr/bin/env python

import pwd
import grp
import os
import stat
import sqlite3

from common import get_bme280_values, DB_PATH


def save_to_db(sensor_id: str, temp: float, hum: float) -> None:
    # open db
    conn = sqlite3.connect(DB_PATH)
    curs = conn.cursor()

    # create table
    curs.execute("CREATE TABLE IF NOT EXISTS temperature (id integer PRIMARY KEY AUTOINCREMENT, timestamp datetime, "
                 "sensor_id text, value numeric);")
    curs.execute("CREATE TABLE IF NOT EXISTS humidity (id integer PRIMARY KEY AUTOINCREMENT, timestamp datetime, "
                 "sensor_id text, value numeric);")

    # add new data
    curs.execute("INSERT INTO temperature (timestamp, sensor_id, value) VALUES "
                 "(datetime(CURRENT_TIMESTAMP, 'localtime'),?,?)", (sensor_id, temp))
    curs.execute("INSERT INTO humidity (timestamp, sensor_id, value) VALUES "
                 "(datetime(CURRENT_TIMESTAMP, 'localtime'),?,?)", (sensor_id, hum))

    # close db
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # get temperature and humidity
    temperature, humidity = get_bme280_values()
    # print(humidity)
    # print(temperature)

    if humidity is not None and temperature is not None:
        save_to_db("1", temperature, humidity)
    else:
        save_to_db("1", -999, -999)

    # make sure the db is owned by www-data
    uid = pwd.getpwnam("www-data").pw_uid
    gid = grp.getgrnam("www-data").gr_gid
    os.chown(DB_PATH, uid, gid)
    os.chmod(DB_PATH, stat.S_IREAD | stat.S_IWRITE | stat.S_IRGRP | stat.S_IWGRP)
