#! /usr/bin/env python3

"""
The following files need to be added to autohumidor/Resources/
    sheet_id.txt -> the google sheets id
    credentials.json -> google sheets api credentials json file. Given when setting up api keys.

Measures temp and humidity for 10 minutes and adds that to the google sheets.
If google sheets addition fails, save the data to a cache.pkl file to be uploaded when internet access is restored.

Run the script every hour to get an hourly reading.

Circuit requires a 4.7K - 10K resistor.
pwr --- resistor --- 3.3v
            |
data --- resistor --- pin 4
ground --------------- ground

Wires
    power - black
    data  - purple
    ground - white
"""

from datetime import datetime
from datetime import timedelta
import os
import re
import statistics as stats
import time
import requests
import pickle
import sys

import Adafruit_DHT

import gspread

resources_file = f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Resources"

if os.path.exists(resources_file) is False:
    os.mkdir(resources_file)

credentials_file = f"{resources_file}/credentials.json"
sheet_id_file = f'{resources_file}/sheet_id.txt'
data_cache_file = f'{resources_file}/cache.pkl'
data_pin = 4

def ht_reading(interval=60):
    """Gives an average reading of humidity and temp for a given time interval (seconds).
    """
    t_end = time.time() + interval
    hum = []
    temp = []
    while time.time() < t_end:
        try:
            humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT22, data_pin)
            hum.append(humidity)
            temp.append(temperature)
        except RuntimeError:
            pass
        time.sleep(2)
    hum = [x for x in hum if x is not None]
    temp = [x for x in temp if x is not None]
    if len(hum) > 0 and len(temp) > 0:
        # Use median values are sometimes bonkers big numbers are made, especially for humidity.
        return round(stats.median(hum), 2), round(stats.median(temp), 2)
    else:
        return None, None


class PostToSheets:
    """
    From data.pkl, post the data to google sheets, in chronological order
    """

    def __init__(self, sheet_name, SHEET_ID):
        self.SCOPE = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        self.SHEET_ID = SHEET_ID
        sa = gspread.service_account(filename=credentials_file)
        sh = sa.open('Humidor')
        self.sheet = sh.sheet1
        self.all_values = self.sheet.get_all_values()

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
        next_free_row = len(self.all_values) + 1
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

    def last_row(self):
        """Returns the last row in the sheet as a list"""
        if len(self.all_values) == 0:
            return None
        return self.all_values[-1]

    def fill_in_nan(self, next_posted_hour):
        """If there has been some error and data is missing, fill in the =na() for each missing data point"""
        # Get last item. If the last item is not one hour behind the next hour to be posted, fill in the rest with na()
        last_hour = self.last_row()
        if last_hour is None:
            # If there is no data in the sheet, just do nothing.
            return None
        last_hour = last_hour[0]
        last_hour = datetime.strptime(last_hour, "%d/%m/%Y %H:00:00")
        next_posted_hour = datetime.strptime(next_posted_hour, "%d/%m/%Y %H:00:00")
        hours_between = (next_posted_hour - last_hour).seconds/60/60

        if hours_between > 1:
            data_to_post = []
            hour = last_hour + timedelta(hours=1)
            while hour < next_posted_hour:
                data_to_post.append([hour.strftime("%d/%m/%Y %H:00:00"), "=na()", "=na()"])
                hour += timedelta(hours=1)
            self.post_data(data_to_post)
            return data_to_post
        else:
            return None


def main():
    args = sys.argv
    if len(args) > 1 and args[1].isdigit():
        h, t = ht_reading(60 * int(args[1]))
    else:
        h, t = ht_reading(60 * 10)  # 10 minutes of readings.
    if h is None or t is None:
        h = '=na()'
        t = '=na()'

    now = datetime.now()
    current_time = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour).strftime("%d/%m/%Y %H:00:00")
    data_to_post = [current_time, str(h), str(t)]

    # Init the cache file if needed.
    if os.path.exists(data_cache_file) is False:
        with open(data_cache_file, 'wb') as f:
            pickle.dump([], f)

    # Open cache file, probably is empty list.
    with open(data_cache_file, 'rb') as f:
        cache_data = pickle.load(f)

    # Append cache to read data.
    cache_data.append(data_to_post)
    data_to_post = cache_data

    if requests.get('http://www.google.com').status_code == 200:
        with open(sheet_id_file, 'r') as f:
            sheet_id = f.read()
        sheet = PostToSheets('Humidor', sheet_id)
        sheet.fill_in_nan(current_time)
        sheet.post_data(data_to_post)
    else:
        with open(data_cache_file, 'wb') as f:
            pickle.dump(data_to_post, f)


if __name__ == '__main__':
    main()
