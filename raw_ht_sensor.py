#! /usr/bin/python3

"""
Measures humid and temp for a 10 second average and pushes to data.json in
{datetime.datetime.now(): {'Humidity': h, 'Temperature': t} } format
"""

import adafruit_dht
import board
import statistics as stats
import time

dht = adafruit_dht.DHT22(board.D4)


def ht_reading(interval=60):
    """Gives an average reading of humidity and temp for a given time interval (seconds).
    """
    t_end = time.time() + interval
    hum = []
    temp = []
    while time.time() < t_end:
        temperature = dht.temperature   # Takes an indeterminant amount of time to return value.
        humidity = dht.humidity
        hum.append(humidity)
        temp.append(temperature)
    if len(hum) > 0 and len(temp) > 0:
        return round(stats.mean(hum), 2), round(stats.mean(temp), 2)
    else:
        return None, None


if __name__ == '__main__':
    print(ht_reading(60))
