#!/usr/bin/env python

import time
import datetime
import arrow
import sqlite3

from flask import Flask, request, render_template

from common import DB_PATH, get_bme280_values

app = Flask(__name__)
app.debug = True


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/temp")
def get_temp():
    temperature, humidity = get_bme280_values()
    if humidity is not None and temperature is not None:
        return render_template("temp.html", temp=temperature, hum=humidity)
    else:
        return render_template("no_sensor.html")


@app.route("/temp_db", methods=['GET'])
def get_temp_db():
    temperature_list, humidity_list, timezone, from_date_str, to_date_str = get_records()

    # Create new record tables so that datetimes are adjusted back to the user browser's time zone.
    time_adjusted_temperature_list = []
    time_adjusted_humidity_list = []
    for record in temperature_list:
        local_timedate = arrow.get(record[1], "YYYY-MM-DD HH:mm:ss").to(timezone)
        time_adjusted_temperature_list.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[3], 2)])

    for record in humidity_list:
        local_timedate = arrow.get(record[1], "YYYY-MM-DD HH:mm:ss").to(timezone)
        time_adjusted_humidity_list.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[3], 2)])

    print("rendering temp_db.html with: %s, %s, %s" % (timezone, from_date_str, to_date_str))

    return render_template("temp_db.html", timezone=timezone,
                           temp=time_adjusted_temperature_list,
                           hum=time_adjusted_humidity_list,
                           from_date=from_date_str,
                           to_date=to_date_str,
                           temp_items=len(temperature_list),
                           query_string=request.query_string,
                           hum_items=len(humidity_list))


def get_records():
    # Get dates from the URL
    from_date_str = request.args.get('from', time.strftime("%Y-%m-%d 00:00"))
    to_date_str = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))
    timezone = request.args.get('timezone', 'Etc/UTC')
    # get range from form
    range_h_form = request.args.get('range_h', '')
    range_h_int = "None"

    print("REQUEST:")
    print(request.args)

    try:
        range_h_int = int(range_h_form)
    except ValueError:
        print("range_h_form not a number")

    print("Received from browser: %s, %s, %s, %s" % (from_date_str, to_date_str, timezone, range_h_int))

    # Validate date before sending it to the DB
    if not validate_date(from_date_str):
        from_date_str = time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str = time.strftime("%Y-%m-%d %H:%M")
    print('2. From: %s, to: %s, timezone: %s' % (from_date_str, to_date_str, timezone))
    # Create datetime object so that we can convert to UTC from the browser's local time
    from_date_obj = datetime.datetime.strptime(from_date_str, '%Y-%m-%d %H:%M')
    to_date_obj = datetime.datetime.strptime(to_date_str, '%Y-%m-%d %H:%M')

    # If range_h is defined, we don't need the from and to times
    if isinstance(range_h_int, int):
        arrow_time_from = arrow.utcnow().shift(hours=-range_h_int)
        arrow_time_to = arrow.utcnow()
        from_date_utc = arrow_time_from.strftime("%Y-%m-%d %H:%M")
        to_date_utc = arrow_time_to.strftime("%Y-%m-%d %H:%M")
        from_date_str = arrow_time_from.to(timezone).strftime("%Y-%m-%d %H:%M")
        to_date_str = arrow_time_to.to(timezone).strftime("%Y-%m-%d %H:%M")
    else:
        # Convert datetime to UTC so we can retrieve the appropriate records from the database
        from_date_utc = arrow.get(from_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")
        to_date_utc = arrow.get(to_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")

    try:
        conn = sqlite3.connect(DB_PATH)
        curs = conn.cursor()
        curs.execute("SELECT * FROM temperature WHERE timestamp BETWEEN ? AND ?",
                     (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
        temperature_list = curs.fetchall()
        curs.execute("SELECT * FROM humidity WHERE timestamp BETWEEN ? AND ?",
                     (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
        humidity_list = curs.fetchall()
        conn.close()
    except sqlite3.OperationalError:
        temperature_list = []
        humidity_list = []

    return [temperature_list, humidity_list, timezone, from_date_str, to_date_str]


def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
