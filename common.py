#!/usr/bin/env python

import sys
import shlex
import subprocess

from typing import Tuple, Optional, List
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


def bash_exec(command: str, capture_output: bool = True, wait_for_exit: bool = True, timeout: int = None)\
        -> Tuple[Optional[int], Optional[str], str]:
    if wait_for_exit is False and timeout is not None:
        raise RuntimeError('Unable to not wait for exit but still have a timeout!')
    if capture_output is True and wait_for_exit is False:
        raise RuntimeError('Unable to not wait for exit but still capture output!')
    command = shlex.split(command)
    assert type(command) == list
    print("Executing: '{}'.".format(" ".join(command)))
    try:
        # set input and output
        if capture_output:
            std_args = {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE}
        elif wait_for_exit is False:
            std_args = {'stdin': None, 'stdout': None, 'stderr': None}
        else:
            std_args = {'stdin': sys.stdin, 'stdout': sys.stdout, 'stderr': sys.stderr}

        # exec
        if timeout:
            process = subprocess.run(command, timeout=timeout, **std_args)
        else:
            process = subprocess.Popen(command, **std_args)

        # get output
        process_output = None
        process_error = None
        if capture_output:
            process_output = process.stdout.decode("utf-8")  # explicit conversion from bytearray to string
            process_error = process.stderr.decode("utf-8")  # explicit conversion from bytearray to string
        return_code = process.returncode
    except (OSError, subprocess.CalledProcessError) as exception:
        print(exception)
        print('Exception occurred: ' + str(exception))
        print('Executing of command failed.')
        return None, None, str(exception)
    return return_code, process_output, process_error
