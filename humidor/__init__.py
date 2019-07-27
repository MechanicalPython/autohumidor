#! /usr/bin/python3

from slackclient import SlackClient
import os


starterbot_id = None
channel = "mattpihumidor"

resources_file = f"{os.path.abspath(__file__).split('/humidor')[0]}/Resources"

data_file = "{}/data.pkl".format(resources_file)
posting_file = "{}/posting.pkl".format(resources_file)
credentials_file = "{}/credentials.json".format(resources_file)
slack_id = f'{resources_file}/slack_id.txt'


def get_slack_client_id(file=slack_id):
    with open(file, 'r') as f:
        return f.read().strip()


def send_message(message, channel=channel):
    print(message)
    slack_client = SlackClient(str(get_slack_client_id()))
    slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message)

