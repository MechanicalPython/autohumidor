#! /usr/bin/env python3

"""
Measures humid and temp for a 10 second average and pushes to data.json in
{datetime.datetime.now(): {'Humidity': h, 'Temperature': t} } format
"""

from datetime import datetime
import os
import re
import statistics as stats
import time

import Adafruit_DHT as dht
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from slackclient import SlackClient

resources_file = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Resources"

if os.path.exists(resources_file) is False:
    os.mkdir(resources_file)

credentials_file = f"{resources_file}/credentials.json"
slack_id_file = f'{resources_file}/slack_id.txt'
sheet_id_file = f'{resources_file}/sheet_id.txt'

channel = "mattpihumidor"

sensor = 22
pin = 4


def send_slack(message, channel=channel):
    with open(slack_id_file, 'r') as f:
        slack_id = f.read().strip()
    slack_client = SlackClient(str(slack_id))
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=message)


def ht_reading(interval=60):
    """Gives an average reading of humidity and temp for a given time interval (seconds).
    """
    t_end = time.time() + interval
    hum = []
    temp = []
    while time.time() < t_end:
        humidity, temperature = dht.read_retry(sensor, pin)  # Takes an indeterminant amount of time to return value.
        hum.append(humidity)
        temp.append(temperature)
    if len(hum) > 0 and len(temp) > 0:
        return round(stats.mean(hum), 2), round(stats.mean(temp), 2)
    else:
        return None, None


class PostToSheets:
    """
    From data.pkl, post the data to google sheets, in chronological order
    """

    def __init__(self, sheet_name, SHEET_ID):
        self.SCOPE = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        self.SHEET_ID = SHEET_ID
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.SCOPE)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open(sheet_name).sheet1

    def post_data(self, data):
        """
        data shape must be row, column
        a  b  c
        d  e  f
        should be: [[a. b, c], [d, e, f]]
        :param data:
        :return:
        """
        # Check for enough room in spreadsheet
        num_rows = len(data)
        max_rows = self.sheet.row_count
        next_free_row = len(self.sheet.col_values(1)) + 1
        if num_rows + next_free_row > max_rows:
            self.sheet.add_rows(num_rows + 10)  # Adds more rows if needed.

        for row in data:
            column = 1
            for item in row:
                try:
                    self.sheet.update_cell(next_free_row, column, item)
                    time.sleep(1)
                except Exception as e:
                    if re.search('"code": 429', str(e)):
                        time.sleep(100)
                column += 1
                time.sleep(1.1)  # To avoid the 100 requests per 100 seconds limit
            next_free_row += 1


def main():
    h, t = ht_reading(60 * 5)  # 5 minutes of readings.
    if h is None or t is None:
        h = '=na()'
        t = '=na()'

    now = datetime.now()
    current_time = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour).strftime("%d/%m/%Y %H:00:00")
    with open(sheet_id_file, 'r') as f:
        sheet_id = f.read()
    PostToSheets('Humidor', sheet_id).post_data([[current_time, str(h), str(t)]])


if __name__ == '__main__':
    main()
