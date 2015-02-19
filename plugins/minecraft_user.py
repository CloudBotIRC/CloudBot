import re
import requests
import uuid

from cloudbot import hook


HIST_API = "http://api.fishbans.com/history/{}"
UUID_API = "http://api.goender.net/api/uuids/{}/"


def get_name(uuid):
    # submit the profile request
    request = requests.get(UUID_API.format(uuid))
    data = request.json()
    return data[uuid]


@hook.command("mcuser", "mcpaid", "haspaid")
def mcuser(text, bot):
    """<username> - gets information about the Minecraft user <account>"""
    headers = {'User-Agent': bot.user_agent}
    text = text.strip()

    # check if we are looking up a UUID
    cleaned = text.replace('-', '')
    if re.search(r'^[0-9a-f]{32}\Z$', cleaned, re.I):
        # we are looking up a UUID, get a name.
        try:
            name = get_name(cleaned)
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, KeyError) as e:
            return "Could not get username from UUID: {}".format(e)
    else:
        name = text

    # get user data from fishbans
    try:
        request = requests.get(HIST_API.format(requests.utils.quote(name)), headers=headers)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get profile status: {}".format(e)

    # read the fishbans data
    try:
        results = request.json()
    except ValueError:
        return "Could not parse profile status"

    # check for errors from fishbans and handle them
    if not results['success']:
        if results['error'] == "User is not premium.":
            return "The account \x02{}\x02 is not premium or does not exist.".format(text)
        else:
            return results['error']

    username = results['data']['username']
    id = uuid.UUID(results['data']['uuid'])

    return 'The account \x02{}\x02 ({}) exists. It is a \x02paid\x02' \
           ' account.'.format(username, id)
