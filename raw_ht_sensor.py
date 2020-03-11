#! /usr/bin/python3

"""
Measures humid and temp for a 10 second average and pushes to data.json in
{datetime.datetime.now(): {'Humidity': h, 'Temperature': t} } format
"""

import time
import board
import adafruit_dht
import statistics as stats
import sys


def ht_reading(interval=60):
    """Gives an average reading of humidity and temp for a given time interval (seconds).
    """
    dht = adafruit_dht.DHT22(board.D18)
    t_end = time.time() + interval
    hum = []
    temp = []
    while time.time() < t_end:
        try:
            temperature = dht.temperature   # Takes an indeterminant amount of time to return value.
            humidity = dht.humidity
            hum.append(humidity)
            temp.append(temperature)
        except RuntimeError:
            pass
    if len(hum) > 0 and len(temp) > 0:
        return round(stats.mean(hum), 2), round(stats.mean(temp), 2)
    else:
        return None, None


def continuous_reading():
    dht = adafruit_dht.DHT22(board.D18)
    while True:
        t = dht.temperature  # Takes an indeterminant amount of time to return value.
        h = dht.humidity
        print(f'Humitidy: {h}, temp {t}')


if __name__ == '__main__':
    args = sys.argv
    if len(args) == 1:
        h, t = ht_reading(60)  # 10 minutes of readings.
        print(f'Humitidy: {h}, temp {t}')
    else:
        if args[1].isdigit():
            h, t = ht_reading(int(args[1]))
        elif args[1] == '-c':
            continuous_reading()


