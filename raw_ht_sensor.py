#! /usr/bin/python3

"""
Measures humid and temp for a 10-second average and pushes to data.json in
{datetime.datetime.now(): {'Humidity': h, 'Temperature': t} } format
"""

import time
from humidor import ht_sensor


def continuous_reading():
    while True:
        try:
            h, t = ht_sensor.ht_reading(2)
            print(f'Humitidy: {h}, temp {t}')
        except RuntimeError as error:
            print(error.args[0])
        time.sleep(2.0)


if __name__ == '__main__':
    continuous_reading()


