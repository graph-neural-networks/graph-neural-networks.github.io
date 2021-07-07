import os
import yaml
import json
import requests

########################################################
#### Script for adding custom emojis for Rocket chat ###
########################################################

# define which API version to use
API_path = "/api/v1/"

# load configuration with authentication tokens for Rocket chat server
config = yaml.safe_load(open("config.yml"))
# convert to header for use with requests later
headers = {
    "X-Auth-Token": config["auth_token"],
    "X-User-Id": config["user_id"],
}

# directory where custom emojis are stored as image files (JPG, PNG, GIF are currently supported)
custom_emoji_dir = "images-custom-emojis/"

# get all emoji images - only include JPG, PNG, and GIF files
emoji_files = [
    x
    for x in os.listdir(custom_emoji_dir)
    if x.endswith(".png") or x.endswith(".jpg") or x.endswith(".gif")
]

for emoji_f in emoji_files:
    emoji_name, emoji_aliases = emoji_f.split(".")[0].split("_")

    files = {
        "emoji": (emoji_f, open(custom_emoji_dir + emoji_f, "rb")),
        "name": (None, emoji_name),
        "aliases": (None, emoji_aliases),
    }
    try:
        response = requests.post(
            config["server"] + API_path + "emoji-custom.create",
            headers=headers,
            files=files,
        )
        response.raise_for_status()
        print(json.loads(response.content)["success"])
    except requests.exceptions.HTTPError as err:
        print("Encountered error: ", err)
        print("File: ", emoji_f)
