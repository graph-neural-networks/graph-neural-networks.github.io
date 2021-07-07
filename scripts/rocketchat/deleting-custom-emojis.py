import os
import yaml
import json
import requests

##########################################################
#### Script for deleting custom emojis for Rocket chat ###
##########################################################

# define which API version to use
API_path = "/api/v1/"

# load configuration with authentication tokens for Rocket chat server
config = yaml.safe_load(open("config.yml"))
# convert to header for use with requests later
headers = {
    "X-Auth-Token": config["auth_token"],
    "X-User-Id": config["user_id"],
}

# get all custom emojis on server right now
response = requests.get(
    config["server"] + API_path + "emoji-custom.list", headers=headers
)
response_emojis = json.loads(response.content)["emojis"]["update"]
current_custom_emojis = [x["_id"] for x in response_emojis]

# update headers
headers["Content-type"] = "application/json"

# delete one by one
for emoji_id in current_custom_emojis:
    data = '{ "emojiId": "' + emoji_id + '" }'
    try:
        response = requests.post(
            config["server"] + API_path + "emoji-custom.delete",
            headers=headers,
            data=data,
        )
        print(json.loads(response.content)["success"])
    except requests.exceptions.HTTPError as err:
        print("Encountered error: ", err)
