import re

import requests
import json

from cloudbot import hook


HIST_API = "http://api.fishbans.com/history/{}"
UUID_API = "http://api.goender.net/api/uuids/{}/"


class McuError(Exception):
    pass


def get_name(uuid):
    # submit the profile request
    try:
        request = requests.get(UUID_API.format(uuid))
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise McuError("Could not get profile status: {}".format(e))

    data = request.json()
    print(data[uuid])

    return data[uuid] or None


@hook.command("mcuser", "mcpaid", "haspaid")
def mcuser(text, bot):
    """<username> - gets information about the Minecraft user <account>"""
    headers = {'User-Agent': bot.user_agent}
    user = text.strip()

    cleaned = user.replace('-', '')
    if re.search(r'[0-9a-f]{32}\Z', cleaned, re.I):
        try:
            name = get_name(cleaned)
        except McuError as e:
            return "Error: {}".format(e)
    else:
        name = user


    if not name:
        return "The account \x02{}\x02 does not exist.".format(user)

    # submit the profile request
    try:
        request = requests.get(HIST_API.format(requests.utils.quote(name)), headers=headers)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get profile status: {}".format(e)

    # get the fishbans data
    try:
        results = request.json()
    except ValueError:
        return "Could not parse profile status"

    # handle errors
    if not results['success']:
        if results['error'] == "User is not premium.":
            return "User is not premium or does not exist."
        else:
            return results['error']

    user = results["data"]

    return 'The account \x02{username}\x02 ({uuid}) exists. It is a \x02paid\x02' \
           ' account.'.format(**user)