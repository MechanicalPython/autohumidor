#! /usr/bin/python3

"""Will collect data.json data every 24 hours at 1am, summarise it, tear down the data.json and set a fresh file

"""

import pickle
import os.path
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import statistics
from slackclient import SlackClient
import datetime
import time
import re
from humidor import get_slack_client_id, send_message


resources_file = "{}/Resources".format(os.path.abspath(__file__).split('/humidor')[0])

data_file = "{}/data.pkl".format(resources_file)
posting_file = "{}/posting.pkl".format(resources_file)
credentials_file = "{}/credentials.json".format(resources_file)
# If modifying these scopes, delete the file token.pickle.
SCOPE = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SHEET_ID = '1abiI71WJp8_iHEYXMEB4F183ekOWFP1IXfWYFjxK-8s'

creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file,
                                                         SCOPE)
client = gspread.authorize(creds)
sheet = client.open('Humidor').sheet1

slack_client = SlackClient(get_slack_client_id())
starterbot_id = None
channel = "mattpihumidor"
RTM_READ_DELAY = 1  # 1 sec delay between reading from RTM


def split_data():
    """Opens data.pkl, splits raw data and this hour data and saves them to post_data.pkl and data.pkl."""
    with open(data_file, 'rb') as f:
        raw_data = pickle.load(f)
    opening_time = datetime.datetime.now()
    # raw_data in {time stamp: {'Humidity': h, 'Temperature': t}}
    # Get list of times. Order it. Iterate through pulling the date and hour. Split into hour groups
    posting_raw = {}  # Format: {YYYY-mm-dd H:00:00: {'H': ls of H, 'T': ls of T}}
    this_hour_raw = {}
    for time, h_t in sorted(raw_data.items()):
        date = "{}-{}-{} {}:00:00".format(time.year, time.month, time.day, time.hour)
        if date == '{}-{}-{} {}:00:00'.format(opening_time.year, opening_time.month, opening_time.day, opening_time.hour):
            this_hour_raw.update({time: h_t})
        else:
            posting_raw.update({time: h_t})
    # Save the files to posting.pkl and data.pkl
    with open(f'{resources_file}/thishour.pkl', 'wb') as f:
        pickle.dump(this_hour_raw, f)
    with open(posting_file, 'wb') as f:
        pickle.dump(posting_raw, f)


def post_data(posting_data):
    """
    Input raw data from posting.pkl, convert the times to string,
    [{'Tmax': 60, 'H': 20, 'Tmin': 70, 'Hour': 10, 'T': 50, 'Hmax': 30, 'Hmin': 40},]
    list of dicts. Each list element is a row. 
    """
    # Convert raw to dict of hours and lists of raw H and T
    times = {}
    for dtime, h_t in sorted(posting_data.items()):
        date = "{}-{}-{} {}:00:00".format(dtime.year, dtime.month, dtime.day, dtime.hour)
        h = h_t['Humidity']
        t = h_t['Temperature']
        if date in times.keys():
            times[date]['H'].append(h)
            times[date]['T'].append(t)
        else:
            times.update({date: {'H': [h], 'T': [t]}})

    # Find min, max and median of raw data
    data = []
    for dtime, h_t in sorted(times.items()):
        h = h_t['H']
        t = h_t['T']
        Hmean = round(statistics.median(h), 2)
        Hmax = round(max(h), 2)
        Hmin = round(min(h), 2)
        Tmean = round(statistics.median(t), 2)
        Tmax = round(max(t), 2)
        Tmin = round(min(t), 2)
        data.append({'Hour': dtime, 'H': Hmean, 'Hmax': Hmax, 'Hmin': Hmin, 'T': Tmean, 'Tmax': Tmax, 'Tmin': Tmin})

    # Post data to sheets
    num_rows = len(data)
    max_rows = sheet.row_count
    next_free_row = len(sheet.col_values(1)) + 1
    if num_rows + next_free_row > max_rows:
        sheet.add_rows(num_rows+10)  # Adds more rows if needed.
        send_message('Running out of room on spreadsheet')

    # Get order of hours
    hours = [d['Hour'] for d in data]
    hours.sort()
    dict_data = {}
    data = [dict_data.update({hour['Hour']: hour}) for hour in data]
    for hour in hours:  # dict_data - {hour: {'Hour': hour, 'T': int, ...
        row = dict_data[hour]
        rowdata = [row['Hour'], row['H'], row['Hmax'], row['Hmin'], row['T'], row['Tmax'], row['Tmin']]
        column_num = 1 
        for item in rowdata:
            notposted = True
            while notposted:
                try:
                    sheet.update_cell(next_free_row, column_num, item)  # (row, column, value)
                    notposted = False
                except Exception as e:
                    if re.search('"code": 429', str(e)):
                        time.sleep(100)
            time.sleep(1.1)  # To avoid the 100 requests per 100 seconds limit
            column_num = column_num + 1
        next_free_row += 1

    os.remove(posting_file)


def main():
    send_message('Sheet bot is posting data', channel)

    try:
        split_data()  # Split raw data into two files: posting data and thishour.pkl to leave alone
        with open(posting_file, 'rb') as post_file:
            data_to_post = pickle.load(post_file)
        post_data(data_to_post)
        # Successful posting of data
        os.rename(f'{resources_file}/thishour.pkl', data_file)  # Effectively resets data.pkl
    except Exception as e:
        send_message(f'Error: sheet bot failed to post data {e}', channel)


if __name__ == '__main__':
    main()
