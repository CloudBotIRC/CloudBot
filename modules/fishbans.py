from urllib.parse import quote_plus

from cloudbot import hook, http, formatting

api_url = "http://api.fishbans.com/stats/{}/"


@hook.command(["bans", "fishbans"])
def fishbans(text):
    """fishbans <user> -- Gets information on <user>s minecraft bans from fishbans"""
    user = text.strip()

    try:
        request = http.get_json(api_url.format(quote_plus(user)))
    except (http.HTTPError, http.URLError) as e:
        return "Could not fetch ban data from the Fishbans API: {}".format(e)

    if not request["success"]:
        return "Could not fetch ban data for {}.".format(user)

    user_url = "http://fishbans.com/u/{}/".format(user)
    ban_count = request["stats"]["totalbans"]

    if ban_count == 1:
        return "The user \x02{}\x02 has \x021\x02 ban - {}".format(user, user_url)
    elif ban_count > 1:
        return "The user \x02{}\x02 has \x02{}\x02 bans - {}".format(user, ban_count, user_url)
    else:
        return "The user \x02{}\x02 has no bans - {}".format(user, user_url)


@hook.command
def bancount(text):
    """bancount <user> -- Gets a count of <user>s minecraft bans from fishbans"""
    user = text.strip()

    try:
        request = http.get_json(api_url.format(quote_plus(user)))
    except (http.HTTPError, http.URLError) as e:
        return "Could not fetch ban data from the Fishbans API: {}".format(e)

    if not request["success"]:
        return "Could not fetch ban data for {}.".format(user)

    user_url = "http://fishbans.com/u/{}/".format(user)
    services = request["stats"]["service"]

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
