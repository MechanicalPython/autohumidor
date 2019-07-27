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

slack_client = SlackClient("xoxb-632926840213-621523016211-vkNfaH2txVQfBRDBKZscIVoQ")
starterbot_id = None
channel = "mattpihumidor"
RTM_READ_DELAY = 1  # 1 sec delay between reading from RTM
sensor = 22 
pin = 4
dir_path = os.path.dirname(os.path.realpath(__file__))
data_file = "{}/data.pkl".format(dir_path)
logging.basicConfig(filename='{}/log.log'.format(dir_path))


def send_message(message, channel):
    slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message)


def ht_reading(interval=10):
    # Gives an average reading of humidity and temp for a given time interval (seconds). Multiple of 2 best
    t_end = time.time() + interval
    hum = []
    temp = []
    while time.time() < t_end:
        humidity, temperature = dht.read_retry(sensor, pin)
        hum.append(humidity)
        temp.append(temperature)
    return round(stats.mean(hum), 2), round(stats.mean(temp), 2)


def write_to_file(data_to_append):
    if os.path.exists(os.path.abspath(data_file)) is False:
        with open(data_file, 'wb') as f:
            pickle.dump(data_to_append, f)
    elif os.stat(data_file).st_size == 0:
        with open(data_file, 'wb') as f:
            pickle.dump(data_to_append, f)

    else:
        with open(data_file, 'rb') as f:
            data = pickle.load(f)
        data_to_append.update(data)
                
        with open(data_file, 'wb') as f:
            pickle.dump(data_to_append, f)

def main():
    is_error = False
    while True:
        try:
            h, t = ht_reading()  # AdaFruit_DHT will return None if no sensor data that gives a TypeError when handeling stats.mean
            timenow = datetime.datetime.now()
            write_to_file({timenow: {'Humidity': h, 'Temperature': t}})
            if is_error is True:  # Only gets to this point if there is an error so if there has been an error the flag is True so it will notify there is no longer an error. 
                send_message('Error with HDT22 sensor has been resolved.', channel)
                is_error = False
        except TypeError:
            if is_error is False:  # Send message if first time there is an error
                send_message('ERROR with HDT22 sensor. No values being returned. Will retry every 10 minutes until fixed', channel)
                is_error = True
            time.sleep(60*10)

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            send_message('HT sensor Error: {}'.format(e), channel)
            logging.error('HT sensor error', exc_info=True)
            time.sleep(10)

