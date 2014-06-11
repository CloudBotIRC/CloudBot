from enum import Enum

import requests
import json

from cloudbot import hook, http


NAME_URL = "https://account.minecraft.net/buy/frame/checkName/{}"
PROFILE_URL = "https://api.mojang.com/profiles/page/1"
PAID_URL = "http://www.minecraft.net/haspaid.jsp"


# enums - "because I can"
NameStatus = Enum('NameStatus', 'free taken invalid')


class McuError(Exception):
    pass


def get_status(name):
    """ takes a name and returns status """
    try:
        name_encoded = http.quote_plus(name)
        request = requests.get(NAME_URL.format(name_encoded))
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise McuError("Could not get name status: {}".format(e))

    # return status as an enum
    if "OK" in request.text:
        return NameStatus.free
    elif "TAKEN" in request.text:
        return NameStatus.taken
    elif "invalid characters" in request.text:
        return NameStatus.invalid


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

    print(results)

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

    try:
        # get status of name (does it exist?)
        status = get_status(user)
    except McuError as e:
        return e

    if status is NameStatus.taken:
        try:
            # get information about user
            profile = get_profile(user)
        except McuError as e:
            return "Error: {}".format(e)

        profile["lt"] = ", legacy" if profile["legacy"] else ""

        if profile["paid"]:
            return "The account \x02{name}\x02 ({id}{lt}) exists. It is a \x02paid\x02" \
                   " account.".format(**profile)
        else:
            return "The account \x02{name}\x02 ({id}{lt}) exists. It \x034\x02is NOT\x02\x0f a paid" \
                   " account.".format(**profile)
    elif status is NameStatus.free:
        return "The account \x02{}\x02 does not exist.".format(user)
    elif status is NameStatus.invalid:
        return "The name \x02{}\x02 contains invalid characters.".format(user)
    else:
        return "The account \x02{}\x02 does not exist.".format(user)
