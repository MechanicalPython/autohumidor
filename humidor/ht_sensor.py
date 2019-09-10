#! /usr/bin/env python3

"""
Measures humid and temp for a 10 second average and pushes to data.json in
{datetime.datetime.now(): {'Humidity': h, 'Temperature': t} } format
"""

import time
import Adafruit_DHT as dht
import statistics as stats
import pickle
import datetime
from slackclient import SlackClient
import os

resources_file = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Resources"

if os.path.exists(resources_file) is False:
    os.mkdir(resources_file)


data_file = f"{resources_file}/data.pkl"
posting_file = f"{resources_file}/posting.pkl"
credentials_file = f"{resources_file}/credentials.json"
slack_id = f'{resources_file}/slack_id.txt'

channel = "mattpihumidor"


def get_slack_client_id(file=slack_id):
    with open(file, 'r') as f:
        return f.read().strip()


def send_message(message, channel=channel):
    slack_client = SlackClient(str(get_slack_client_id()))
    slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message)


sensor = 22
pin = 4


def ht_reading(interval=60):
    """Gives an average reading of humidity and temp for a given time interval (seconds).
    """
    t_end = time.time() + interval
    hum = []
    temp = []
    while time.time() < t_end:
        humidity, temperature = dht.read_retry(sensor, pin)
        hum.append(humidity)
        temp.append(temperature)
    return round(stats.mean(hum), 2), round(stats.mean(temp), 2)


def write_to_file(data_to_append):
    """Writes data to data.pkl
    """
    with open(data_file, 'rb') as f:
        data = pickle.load(f)
    data_to_append.update(data)
    with open(data_file, 'wb') as f:
        pickle.dump(data_to_append, f)


def main():
    # If data file does not exist, make one.
    if os.path.exists(os.path.abspath(data_file)) is False or os.stat(data_file).st_size == 0:
        with open(data_file, 'wb') as f:
            pickle.dump({}, f)
    try:
        send_message('HDT22 sensor is now online')
    except Exception:
        pass
    while True:
        try:
            h, t = ht_reading()  # AdaFruit_DHT will return None if no sensor data that gives a TypeError when handeling stats.mean
            timenow = datetime.datetime.now()
            write_to_file({timenow: {'Humidity': h, 'Temperature': t}})
        except TypeError:
            send_message('ERROR with HDT22 sensor. No values being returned. Will retry in 5 minutes.')
            time.sleep(60*5)


if __name__ == '__main__':
    main()
