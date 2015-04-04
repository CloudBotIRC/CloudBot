from urllib.parse import quote_plus

import requests
import requests.exceptions

from cloudbot import hook
from cloudbot.util import formatting

api_url = "http://api.fishbans.com/stats/{}/"


@hook.command("bans", "fishbans")
def fishbans(text, bot):
    """<user> - gets information on <user>'s minecraft bans from fishbans"""
    user = text.strip()
    headers = {'User-Agent': bot.user_agent}

    try:
        request = requests.get(api_url.format(quote_plus(user)), headers=headers)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not fetch ban data from the Fishbans API: {}".format(e)

    try:
        json = request.json()
    except ValueError:
        return "Could not fetch ban data from the Fishbans API: Invalid Response"

    if not json["success"]:
        return "Could not fetch ban data for {}.".format(user)

    user_url = "http://fishbans.com/u/{}/".format(user)
    ban_count = json["stats"]["totalbans"]

    if ban_count == 1:
        return "The user \x02{}\x02 has \x021\x02 ban - {}".format(user, user_url)
    elif ban_count > 1:
        return "The user \x02{}\x02 has \x02{}\x02 bans - {}".format(user, ban_count, user_url)
    else:
        return "The user \x02{}\x02 has no bans - {}".format(user, user_url)


@hook.command()
def bancount(text, bot):
    """<user> - gets a count of <user>'s minecraft bans from fishbans"""
    user = text.strip()
    headers = {'User-Agent': bot.user_agent}

    try:
        request = requests.get(api_url.format(quote_plus(user)), headers=headers)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not fetch ban data from the Fishbans API: {}".format(e)

    try:
        json = request.json()
    except ValueError:
        return "Could not fetch ban data from the Fishbans API: Invalid Response"

    if not json["success"]:
        return "Could not fetch ban data for {}.".format(user)

    user_url = "http://fishbans.com/u/{}/".format(user)
    services = json["stats"]["service"]

    out = []
    for service, ban_count in list(services.items()):
        if ban_count != 0:
            out.append("{}: \x02{}\x02".format(service, ban_count))
        else:
            pass

    if not out:
        return "The user \x02{}\x02 has no bans - {}".format(user, user_url)
    else:
        return "Bans for \x02{}\x02: {} - {}".format(user, formatting.get_text_list(out, "and"), user_url)
