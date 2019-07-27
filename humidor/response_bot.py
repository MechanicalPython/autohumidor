#! /usr/bin/python3

"""
Montor the slack channel and reply with the current humidity and temp to 'report' command
"""

import os
import time
from slackclient import SlackClient
import pickle
from subprocess import call
import logging

slack_client = SlackClient("xoxp-632926840213-632926840389-694220006997-414cbc735e7d51026159168a934ddaa8")
starterbot_id = None
channel = "mattpihumidor"
RTM_READ_DELAY = 1  # 1 sec delay between reading from RTM
dir_path = os.path.dirname(os.path.realpath(__file__))
data_file = "{}/data.pkl".format(dir_path)

logging.basicConfig(filename='{}/log.log'.format(dir_path))

def send_message(message, channel):
    slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message)

def get_latest_reading():
    data = None
    while data is None:
        try:
            with open(data_file, 'rb') as f:
                data = pickle.load(f)
        except FileNotFoundError:
            time.sleep(1)
    latest = max(list(data.keys()))
    h = data[latest]['Humidity']
    t = data[latest]['Temperature']
    return h, t
    
def main():
    connected = False
    while connected is False:
        if slack_client.rtm_connect():
            connected = True
            send_message('Response bot is online', channel)
            while True:
                # Read bot user id by calling web API method auth.test
                starterbot_id = slack_client.api_call("auth.test")["user_id"]
                events = slack_client.rtm_read()
                for event in events:
                    if event["type"] == "message" and event["text"].lower() == 'report':
                        h, t = get_latest_reading()
                        send_message('The current humidity and temperature is {}% {}C'.format(h, t), channel)
                    elif event['type'] == 'message' and event['text'].lower() == 'shutdown':
                        call("sudo shutdown -h now", shell=True)
                    elif event['type'] == 'message' and event['text'].lower() == 'reboot':
                        call("sudo reboot", shell=True)
                    elif event['type'] == 'message' and event['text'].lower() == 'hello':
                        send_message('World!', channel)
                    time.sleep(RTM_READ_DELAY)
        else:
            time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error('Exception occured', exc_info=True)
        send_message("Reponse Bot had an error: {}".format(e))
