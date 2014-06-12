from enum import Enum

import requests
import json
import re

from cloudbot import hook, http


# I need TREE apis, all on separate domains, to get basic account info
# what the fuck, mojang?
UUID_URL = "https://sessionserver.mojang.com/session/minecraft/profile/{}"
PROFILE_URL = "https://api.mojang.com/profiles/page/1"
PAID_URL = "http://www.minecraft.net/haspaid.jsp"



class McuError(Exception):
    pass


def get_name(uuid):
    """ takes a UUID and finds the associated name """
    uuid_encoded = http.quote_plus(uuid)

    try:
        request = requests.get(UUID_URL.format(uuid_encoded))
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise McuError("Could not get name from UUID: {}".format(e))

    # get the JSON data
    try:
        results = request.json()
    except ValueError:
        raise McuError("Could not get name from UUID")

    print(results)
    # check for errors
    if "error" in results:
        return False
    else:
        return results["name"]


def get_profile(name):
    profile = {}

    # form the profile request
    payload = {
        "name": name,
        "agent": "minecraft"
    }

    # submit the profile request
    try:
        headers = {"Content-Type": "application/json"}
        request = requests.post(PROFILE_URL, data=json.dumps(payload).encode('utf-8'), headers=headers)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise McuError("Could not get profile status: {}".format(e))

    # get the JSON data
    try:
        results = request.json()
    except ValueError:
        raise McuError("Could not parse profile status")

    if results["size"] == 0:
        return False

    user = results["profiles"][0]
    profile["name"] = user["name"]
    profile["id"] = user["id"]

    profile["legacy"] = user.get("legacy", False)

    try:
        params = {'user': name}
        response = requests.get(PAID_URL, params=params)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise McuError("Could not get payment status: {}".format(e))

    if "true" in response.text:
        profile["paid"] = True
    else:
        profile["paid"] = False

    return profile


@hook.command("mcuser", "mcpaid", "haspaid")
def mcuser(text):
    """<username> - gets information about the Minecraft user <account>"""
    user = text.strip()

    cleaned = user.replace('-', '')
    if re.search(r'[0-9a-f]{32}\Z', cleaned, re.I):
        user = get_name(cleaned)

        # UUID could not be matched
        if not user:
            return "Could not find an account using the UUID"

    try:
        # get information about user
        profile = get_profile(user)
    except McuError as e:
        return "Error: {}".format(e)

    if not profile:
        return "The account \x02{}\x02 does not exist.".format(user)

    profile["lt"] = ", legacy" if profile["legacy"] else ""

    if profile["paid"]:
        return 'The account \x02{name}\x02 ({id}{lt}) exists. It is a \x02paid\x02' \
               ' account.'.format(**profile)
    else:
        return 'The account \x02{name}\x02 ({id}{lt}) exists. It \x034\x02is NOT\x02\x0f a paid' \
               ' account.'.format(**profile)
