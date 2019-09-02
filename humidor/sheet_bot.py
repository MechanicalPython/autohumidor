#! /usr/bin/python3

"""Will collect data.json data every 24 hours at 1am, summarise it, tear down the data.json and set a fresh file

"""

import pickle
import os.path
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import statistics
import datetime
import time
import re
from humidor import send_message, data_file, posting_file, credentials_file


class PostToSheets:
    """
    From data.pkl, post the data to google sheets, in chronological order
    """
    def __init__(self):
        self.SCOPE = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        self.SHEET_ID = '1abiI71WJp8_iHEYXMEB4F183ekOWFP1IXfWYFjxK-8s'
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, self.SCOPE)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open('Humidor').sheet1

        with open(data_file, 'rb') as f:
            self.data = pickle.load(f)
        self.posting_data = {}  # Format: {YYYY-mm-dd H:00:00: {'H': ls of H, 'T': ls of T}}
        self.this_hour_raw = {}

    def pull_past_data(self):
        opening_time = datetime.datetime.now()
        for time, h_t in sorted(self.data.items()):
            date = "{}-{}-{} {}:00:00".format(time.year, time.month, time.day, time.hour)
            if date == '{}-{}-{} {}:00:00'.format(opening_time.year, opening_time.month, opening_time.day, opening_time.hour):
                self.this_hour_raw.update({time: h_t})
            else:
                self.posting_data.update({time: h_t})

    def convert_to_posting_format(self):

        # Convert to {hour: {'H': [ls of humiditys], {'T': [ls of temps], ...}
        times = {}
        for dtime, h_t in sorted(self.posting_data.items()):

            date = f"{dtime.year}-{dtime.month}-{dtime.day} {dtime.hour}:00:00"
            h = h_t['Humidity']
            t = h_t['Temperature']

            if date in times.keys():  # Either make or append the data to times
                times[date]['H'].append(h)
                times[date]['T'].append(t)
            else:
                times.update({date: {'H': [h], 'T': [t]}})

        # Get average temp and hum for each hour
        for dtime, h_t in times.items():
            times[dtime]['H'] = round(statistics.median(times[dtime]['H']), 2)
            times[dtime]['T'] = round(statistics.median(times[dtime]['T']), 2)

        return times

    def post_data(self, data):
        """
        post data to
        :param data:
        :return:
        """
        # Check for enough room in spreadsheet
        num_rows = len(data)
        max_rows = self.sheet.row_count
        next_free_row = len(self.sheet.col_values(1)) + 1
        if num_rows + next_free_row > max_rows:
            self.sheet.add_rows(num_rows + 10)  # Adds more rows if needed.
            send_message('Running out of room on spreadsheet')

        # data format: {hour: {'H': mean hum, 'T': mean temp}, }
        # hour format: f"{dtime.year}-{dtime.month}-{dtime.day} {dtime.hour}:00:00"
        sorted_data = sorted(data)
        for hour in sorted_data:
            humidity = data[hour]['H']
            temperature = data[hour]['T']
            # hour = yyyy-m-d hour:00:00

            # column order is hour, humidity, temp
            notposted = True
            while notposted:
                try:
                    self.sheet.update_cell(next_free_row, 1, hour)  # (row, column, value)
                    self.sheet.update_cell(next_free_row, 2, humidity)
                    self.sheet.update_cell(next_free_row, 3, temperature)
                    notposted = False
                except Exception as e:
                    if re.search('"code": 429', str(e)):
                        time.sleep(100)
                time.sleep(1.1)  # To avoid the 100 requests per 100 seconds limit
            next_free_row += 1

    def main(self):
        self.pull_past_data()
        data = self.convert_to_posting_format()
        self.post_data(data)
        # Effectively resets data.pkl
        with open(data_file, 'wb') as write_file:
            pickle.dump(self.this_hour_raw, write_file)


def main():
    send_message('Sheet bot is posting data')

    try:
        PostToSheets().main()
    except Exception as e:
        send_message(f'Error: sheet bot failed to post data {e}')


if __name__ == '__main__':
    PostToSheets().main()
