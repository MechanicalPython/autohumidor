#! /usr/bin/python3


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

resources_file = "{}/Resources".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

data_file = "{}/data.pkl".format(resources_file)
posting_file = "{}/posting.pkl".format(resources_file)
credentials_file = "{}/credentials.json".format(resources_file)
slack_id = '{}/slack_id.txt'.format(resources_file)

starterbot_id = None
channel = "mattpihumidor"
RTM_READ_DELAY = 1  # 1 sec delay between reading from RTM
sensor = 22 
pin = 4


def get_slack_client_id(file=slack_id):
    with open(file, 'r') as f:
        return f.read().strip()


def send_message(message, channel=channel):
    slack_client = SlackClient(str(get_slack_client_id()))
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
    while True:
        try:
            h, t = ht_reading()  # AdaFruit_DHT will return None if no sensor data that gives a TypeError when handeling stats.mean
            timenow = datetime.datetime.now()
            write_to_file({timenow: {'Humidity': h, 'Temperature': t}})
        except TypeError:
            send_message('ERROR with HDT22 sensor. No values being returned. Will retry in 5 minutes.', channel)
            time.sleep(60*5)


if __name__ == '__main__':
    main()
