#!/usr/bin/env python

import os
import sqlite3
import arrow

from common import get_bme280_values, DB_PATH


if __name__ == "__main__":
    if not os.path.isfile(DB_PATH):
        print("There is no database!")
        exit(1)

    range_h_int = 2
    arrow_time_from = arrow.utcnow().shift(hours=-range_h_int)
    arrow_time_to = arrow.utcnow()
    from_date_utc = arrow_time_from.strftime("%Y-%m-%d %H:%M")
    to_date_utc = arrow_time_to.strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect(DB_PATH)
    curs = conn.cursor()
    curs.execute("SELECT * FROM temperature")
    #curs.execute("SELECT * FROM temperature WHERE timestamp BETWEEN ? AND ?", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
    temperature_list = curs.fetchall()
    #curs.execute("SELECT * FROM humidity WHERE timestamp BETWEEN ? AND ?", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
    #humidity_list = curs.fetchall()
    conn.close()

    print(temperature_list)
    #print(humidity_list)
