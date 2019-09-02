#! /usr/bin/python3


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


if __name__ == '__main__':
    send_message('Hello world')

