#! /usr/bin/python3

"""
Measures humid and temp for a 10 second average and pushes to data.json in
{datetime.datetime.now(): {'Humidity': h, 'Temperature': t} } format
"""

import Adafruit_DHT as dht
import os

RTM_READ_DELAY = 1  # 1 sec delay between reading from RTM
sensor = 22 
pin = 4
dir_path = os.path.dirname(os.path.realpath(__file__))
data_file = "{}/data.pkl".format(dir_path)


if __name__ == '__main__':
    dht.read_retry(sensor, pin)
