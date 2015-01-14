import re
import requests

from cloudbot import hook


HIST_API = "http://api.fishbans.com/history/{}"
UUID_API = "http://api.goender.net/api/uuids/{}/"


def get_name(uuid):
    # submit the profile request
    request = requests.get(UUID_API.format(uuid))
    data = request.json()
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
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            return "Could not get username from UUID: {}".format(e)
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
            return "The account \x02{}\x02 is not premium or does not exist.".format(user)
        else:
            return results['error']
    user = results["data"]

    return 'The account \x02{username}\x02 ({uuid}) exists. It is a \x02paid\x02' \
           ' account.'.format(**user)
