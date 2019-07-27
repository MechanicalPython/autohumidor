#! /usr/bin/python3
#ht_snesor.py

"""
Measures humid and temp for a 10 second average and pushes to data.json in
{datetime.datetime.now(): {'Humidity': h, 'Temperature': t} } format
"""
import RPi.GPIO as GPIO
import time
import Adafruit_DHT as dht
import statistics as stats
import pickle
import os
import datetime
from slackclient import SlackClient
import logging

RTM_READ_DELAY = 1  # 1 sec delay between reading from RTM
sensor = 22 
pin = 4
dir_path = os.path.dirname(os.path.realpath(__file__))
data_file = "{}/data.pkl".format(dir_path)
logging.basicConfig(filename='{}/log.log'.format(dir_path))


def interval_ht_reading(interval=10):
    # Gives an average reading of humidity and temp for a given time interval (seconds). Multiple of 2 best
    t_end = time.time() + interval
    hum = []
    temp = []
    while time.time() < t_end:
        humidity, temperature = dht.read_retry(sensor, pin)
        hum.append(humidity)
        temp.append(temperature)
    return hum, temp 


def raw_ht_reading():
    return dht.read_retry(sensor, pin)

if __name__ == '__main__':
    print(interval_ht_reading())
