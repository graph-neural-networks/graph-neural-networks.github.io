# Script to create the channels for the workshops and their papers

from typing import List

import pandas as pd
import yaml
import pdb
import csv
import json

import yaml
from requests import sessions
from rocketchat_API.rocketchat import RocketChat
from mass_delete_rooms import delete_rocketchat_workshop_channels
import time
import sys
import datetime

# from datetime import datetime

WORKSHOPS_YAML = "../../sitedata/workshops.yml"
WORKSHOPS_PAPERS_CSV = "../../sitedata/workshop_papers.csv"
ROCKETCHAT_KEY = "../../scripts/rocketchat/config.yml"


def connect_rocket_API(config, session):
    rocket = RocketChat(
        user_id=config["user_id"],
        auth_token=config["auth_token"],
        server_url=config["server"],
        session=session,
    )
    return rocket


def sleep_session(duration):
    for remaining in range(duration, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)


def create_rocketchat_channels(channel_names):
    with open(ROCKETCHAT_KEY, "r") as f:
        config = yaml.safe_load(f)
    today = datetime.datetime.today() + datetime.timedelta(days=10)
    today = today.strftime("%Y-%m-%dT%H:%M:%S")
    oldest = datetime.datetime.today() + datetime.timedelta(days=-10)
    oldest = oldest.strftime("%Y-%m-%dT%H:%M:%S")
    with sessions.Session() as session:
        rocket = connect_rocket_API(config, session)
        for paper in channel_names:
            channel_name = channel_names[paper]["channel_name"]
            created = rocket.channels_create(channel_name).json()
            if created["success"] == False:  ## Code to handle when API Limit is hit
                print("API rate limit hit, pausing for 1 minute")
                sleep_session(60)
                try:
                    created = rocket.channels_create(channel_name).json()
                except:
                    rocket = connect_rocket_API(config, session)
                    created = rocket.channels_create(channel_name).json()
            print(channel_name, created)
            channel_id = rocket.channels_info(channel=channel_name).json()["channel"][
                "_id"
            ]
            rocket.channels_set_topic(channel_id, channel_names[paper]["topic"]).json()
            rocket.channels_set_description(
                channel_id, channel_names[paper]["description"]
            ).json()
            # pdb.set_trace()
            # rocket.rooms_info(room_name=channel_name)
            # rocket.rooms_clean_history(room_id = channel_id,latest=today,oldest=oldest)
            print(
                "Creating " + channel_name + " topic " + channel_names[paper]["topic"]
            )
            # pdb.set_trace()


def get_workshop_channels():
    with open(WORKSHOPS_YAML, "r") as f:
        workshops = yaml.safe_load(f)
    channels = {}
    # channels_ary = []
    for w in workshops:
        channel_name = w["rocketchat_channel"]
        alias = w["alias"]
        topic = w["title"]
        description = w["abstract"]
        website = w["website"]
        announcement = "%s - %s - %s" % (topic, description, website,)
        channel = {
            "alias": alias,
            "channel_name": channel_name,
            "topic": topic,
            "description": announcement,
        }
        channels[w["UID"]] = channel
        # channels_ary.append(channel)
    return channels  # ,channels_ary


def get_workshop_paper_channels(workshop_channels):

    df = pd.read_csv(WORKSHOPS_PAPERS_CSV)

    channels = {}
    for _, row in df.iterrows():
        paper_id = row["UID"]
        workshop_id = row["workshop"]
        alias = workshop_channels[workshop_id]["alias"]
        workshop_description = workshop_channels[workshop_id]["description"]
        author_string = row["authors"].replace("|", ", ")
        topic = "%s - %s" % (row["title"], author_string,)
        description = "%s - %s" % (topic, workshop_description,)
        channel_name = f"paper-{alias}-{paper_id.split('.')[-1]}"
        channel = {
            "channel_name": channel_name,
            "topic": topic,
            "description": description,
        }
        channels[paper_id] = channel
    return channels


if __name__ == "__main__":
    with open(ROCKETCHAT_KEY, "r") as f:
        config = yaml.safe_load(f)
    workshop_channels = get_workshop_channels()
    workshop_papers = get_workshop_paper_channels(workshop_channels)
    # delete_rocketchat_workshop_channels(workshop_papers,config)
    # create_rocketchat_channels(workshop_channels)
    create_rocketchat_channels(workshop_papers)
