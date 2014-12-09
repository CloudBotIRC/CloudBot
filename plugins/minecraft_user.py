import re

import requests
import json

from cloudbot import hook


HIST_API = "http://api.goender.net/api/hist/page/1"
UUID_API = "http://api.goender.net/api/profiles/page/1"

PAID_URL = "http://www.minecraft.net/haspaid.jsp"


class McuError(Exception):
    pass


def get_uuid(username):
    # form the UUID request
    payload = [{"user": username}]

    # submit the profile request
    try:
        headers = {"Content-Type": "application/json"}
        request = requests.post(UUID_API, data=json.dumps(payload).encode('utf-8'), headers=headers)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise McuError("Could not get profile status: {}".format(e))

    data = request.json()

    return data[username] or None


def get_profile(uuid):
    profile = {}

    # form the UUID request
    payload = [{"uuid": uuid}]

    print(json.dumps(payload))

    # submit the profile request
    try:
        headers = {"Content-Type": "application/json"}
        request = requests.post(HIST_API, data=json.dumps(payload).encode('utf-8'), headers=headers)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise McuError("Could not get profile status: {}".format(e))

    print(request.text)
    # get the JSON data
    try:
        results = request.json()
    except ValueError:
        raise McuError("Could not parse profile status")

    print(results)
    if not results:
        return False

    user = results[0]
    profile["name"] = user["name"]
    profile["id"] = user["id"][0]

    try:
        params = {'user': uuid}
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
        uuid = cleaned
    else:
        try:
            uuid = get_uuid(user)
        except McuError as e:
            return "Error: {}".format(e)

    if not uuid:
        return "The account \x02{}\x02 does not exist.".format(user)

    try:
        # get information about user
        profile = get_profile(uuid)
    except McuError as e:
        return "Error: {}".format(e)

    if not profile:
        return "The account \x02{}\x02 does not exist.".format(user)

    if profile["paid"]:
        return 'The account \x02{name}\x02 ({id}) exists. It is a \x02paid\x02' \
               ' account.'.format(**profile)
    else:
        return 'The account \x02{name}\x02 ({id}) exists. It \x034\x02is NOT\x02\x0f a paid' \
               ' account.'.format(**profile)
