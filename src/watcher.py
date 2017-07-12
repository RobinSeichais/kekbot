# coding: utf8

import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from slackclient import SlackClient


SLACK_API_TOKEN = "xoxb-46813601744-Nn1POLYDxp1yZ79RGeTZtJGO"
POLL_DELAY = 1


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler("/var/log/kekbot/messages",
    when="midnight", utc=False, backupCount=0)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def run():

    client = SlackClient(SLACK_API_TOKEN)

    if not client.rtm_connect():
        print("failed to connect to Slack RTM API")

    while True:
        for message in client.rtm_read():
            handle_message(message)
        time.sleep(POLL_DELAY)


def handle_message(msg):
    if "type" not in msg:
        return
    elif msg["type"] == "message":
        data = format_message(msg)
    elif msg["type"] in ["reaction_added", "reaction_removed"]:
        data = format_reaction(msg)
    else:
        data = None

    if data:
        logger.info(data)
        print(data)


def format_message(msg):
    if "subtype" not in msg:
        return {"message_id": str(msg["ts"]),
            "type": "message",
            "content": msg["text"],
            "user": msg["user"],
            "channel": msg["channel"],
            "ts": msg["ts"]}
    if msg["subtype"] == "message_changed":
        return {"message_id": str(msg["previous_message"]["ts"]),
            "type": "edit",
            "content": msg["message"]["text"],
            "user": msg["message"]["user"],
            "channel": msg["channel"],
            "ts": msg["event_ts"]}
    return None

def format_reaction(msg):
    if msg["type"] == "reaction_added":
        return {"message_id": str(msg["item"]["ts"]),
            "type": "react_add",
            "content": msg["reaction"],
            "user": msg["user"],
            "channel": msg["item"]["channel"],
            "ts": msg["event_ts"]}
    if msg["type"] == "reaction_removed":
        return {"message_id": str(msg["item"]["ts"]),
            "type": "react_del",
            "content": msg["reaction"],
            "user": msg["user"],
            "channel": msg["item"]["channel"],
            "ts": msg["event_ts"]}
    return None


if __name__ == "__main__":
    run()