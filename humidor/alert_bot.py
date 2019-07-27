#! /usr/bin/python3

import os
import time
from slackclient import SlackClient
import pickle
import datetime
import statistics
import logging
import requests

"""
The humidity and temperature is really stable. The sheet bot posts at 1am so at midnight, if the average of that day is outside
65-75 then alert. Each and every time at midnight. 
{datetime: {Humdity: h, 'Temperature': t}
"""

slack_client = SlackClient("xoxp-632926840213-632926840389-694220006997-414cbc735e7d51026159168a934ddaa8")
starterbot_id = None
channel = "mattpihumidor"
RTM_READ_DELAY = 1  # 1 sec delay between reading from RTM
dir_path = os.path.dirname(os.path.realpath(__file__))
data_file = "{}/data.pkl".format(dir_path)
logging.basicConfig(filename='{}/alert_bot.log'.format(dir_path), format='%(asctime)s:%(levelname)s:%(message)s)', level=logging.INFO)


def send_message(message, channel):
    slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message)

def average_humidity():
    # Get data from file
    data = None
    while data is None:
        try:
            with open(data_file, 'rb') as f:
                data = pickle.load(f)
        except FileNotFoundError:
            time.sleep(1)
    all_humidity = []
    all_temp = []
    for time, ht in data.items():
        h = ht['Humidity']
        t = ht['Temperature']
        all_humidity.append(h)
        all_temp.append(t)
    avg_h = round(statistics.mean(all_humidity), 2)
    avg_t = round(statistics.mean(all_temp), 2)
    return avg_h, avg_t

   ### Deprediated ###
   # Get last 5 minutes of data
    #tneg5 = datetime.datetime.now() + datetime.timedelta(minutes=-minutes)
    #last_5_minutes = []
    #while len(last_5_minutes) == 0:
    #    for time in data.keys():
    #        # if time in data is bigger (therefore closer to now) than 5 minutes ago, take it
    #        if datetime.datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S.%f') < tneg5:  # further in past means smaller datetime. Future datetime is bigger. 
     #           last_5_minutes.append(data[time]['Humidity'])

    #return round(statistics.mean(last_5_minutes), 2)


def main():
    if requests.get('http://google.com').status_code != 200:
        quit()
    h, t = average_humidity()
    logging.info('{}% and {}C'.format(h, t))
    if h < 65 or h > 75: # If humid is 70, statement is true.
        send_message('Alert! Humidity is now {}%'.format(h), channel)
    if h < 18 or h > 23:
        send_message('Alert! Temperature is now {}C'.format(t), channel)
        

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error('Alert bot error', exc_info=True)
        send_message('Alert bot error: {}'.format(e), channel)
