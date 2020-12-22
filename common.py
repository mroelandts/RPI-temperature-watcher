#!/usr/bin/env python

from typing import Tuple
from smbus2 import SMBus
from bme280 import BME280

DB_PATH = '/var/www/temp_app/temp_app.db'


def get_bme280_values() -> Tuple[float, float]:
    # Initialise the BME280
    bus = SMBus(1)
    bme280 = BME280(i2c_dev=bus)

    # Set up in "forced" mode
    # In this mode `get_temperature` and `get_pressure` will trigger
    # a new reading and wait for the result.
    # The chip will return to sleep mode when finished.
    bme280.setup(mode="forced")

    temperature = float(round(bme280.get_temperature(), 2))
    humidity = float(round(bme280.get_humidity(), 2))
    return temperature, humidity

