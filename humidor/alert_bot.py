#! /usr/bin/python3.5

import os
import time
import pickle
import datetime
import statistics
from slackclient import SlackClient

channel = "mattpihumidor"

resources_file = "{}/Resources".format(os.path.abspath(__file__).split('/humidor')[0])

data_file = "{}/data.pkl".format(resources_file)
posting_file = "{}/posting.pkl".format(resources_file)
credentials_file = "{}/credentials.json".format(resources_file)
slack_id = '{}/slack_id.txt'.format(resources_file)


def get_slack_client_id(file=slack_id):
    with open(file, 'r') as f:
        return f.read().strip()


def send_message(message, channel=channel):
    slack_client = SlackClient(str(get_slack_client_id()))
    slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message)


def avg_humidity_temp(minutes=5):
    # Get data from file

    with open(data_file, 'rb') as f:
        data = pickle.load(f)
    # Get last 5 minutes of data
    tneg5 = datetime.datetime.now() + datetime.timedelta(minutes=-minutes)
    humidity = []
    temperature = []
    while len(humidity) == 0:
        for time in data.keys():
            # if time in data is bigger (therefore closer to now) than 5 minutes ago, take it
            if datetime.datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S.%f') < tneg5:  # further in past means smaller datetime. Future datetime is bigger. 
                humidity.append(data[time]['Humidity'])
                temperature.append(data[time]['Temperature'])

    return round(statistics.mean(humidity), 2), round(statistics.mean(temperature), 2)


def main():
    try:
        h, t = avg_humidity_temp(60*60*24)
        send_message('Humidity and Tempertaure for past 24 hours: {}% and {}C'.format(h, t), channel)
    except Exception as e:
        send_message('Alert bot main error: {}'.format(e), channel)


if __name__ == '__main__':
    send_message('Hello')
    # main()
