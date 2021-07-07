# Adaptation of the mass channel creation. The script is to delete multiple channels at once from a CSV file
import argparse
import csv
import json

import yaml
from requests import sessions
from rocketchat_API.rocketchat import RocketChat

import time
import sys

import pdb


def parse_arguments():
    parser = argparse.ArgumentParser(description="MiniConf Portal Command Line")
    parser.add_argument("--config", default="config.yml", help="Configuration yaml")
    parser.add_argument("--papers", default="papers.csv", help="Papers CSV")
    parser.add_argument("--test", action="store_true")
    return parser.parse_args()


# Fancy countdown function for sleeping threads
def sleep_session(duration):
    for remaining in range(duration, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)


def read_papers(fname):
    _name, typ = fname.split("/")[-1].split(".")
    if typ == "json":
        res = json.load(open(fname))
    elif typ in {"csv", "tsv"}:
        res = list(csv.DictReader(open(fname)))
    elif typ == "yml":
        res = yaml.load(open(fname).read(), Loader=yaml.SafeLoader)
    else:
        raise ValueError("file not supported: " + fname)
    return res


def connect_rocket_API(config, session):
    rocket = RocketChat(
        user_id=config["user_id"],
        auth_token=config["auth_token"],
        server_url=config["server"],
        session=session,
    )
    return rocket


if __name__ == "__main__":
    args = parse_arguments()

    config = yaml.load(open(args.config))
    papers = read_papers(args.papers)

    with sessions.Session() as session:
        rocket = connect_rocket_API(config, session)

        for paper in papers:
            channel_name = "paper-" + paper["UID"]
            channel_name = channel_name.replace(".", "-")
            if not args.test:

                delete_channel = rocket.channels_delete(channel=channel_name).json()
                if (
                    delete_channel["success"] == False
                ):  ## Code to handle when API Limit is hit
                    print("API rate limit hit, pausing for 1 minute")
                    sleep_session(60)
                    try:
                        delete_channel = rocket.channels_delete(
                            channel=channel_name
                        ).json()
                    except:
                        rocket = connect_rocket_API(config, session)
                        delete_channel = rocket.channels_delete(
                            channel=channel_name
                        ).json()
                print(channel_name, delete_channel)

            print("Deleted " + channel_name)
