from urllib import quote_plus

from util import hook, http


api_url = "http://api.fishbans.com/stats/{}/"


@hook.command("bans")
@hook.command
def fishbans(inp):
    """fishbans <user> -- Gets information on <user>s minecraft bans from fishbans"""
    user = inp.strip()

    try:
        request = http.get_json(api_url.format(quote_plus(user)))
    except (http.HTTPError, http.URLError) as e:
        return "Could not fetch ban data from the Fishbans API: {}".format(e)

    if not request["success"]:
        return "Could not fetch ban data for {}.".format(user)

    user_url = "http://fishbans.com/u/{}/".format(user)
    ban_count = request["stats"]["totalbans"]

    return "The user \x02{}\x02 has \x02{}\x02 ban(s). See detailed info " \
           "at {}".format(user, ban_count, user_url)


@hook.command
def bancount(inp):
    """bancount <user> -- Gets a count of <user>s minecraft bans from fishbans"""
    user = inp.strip()

    try:
        request = http.get_json(api_url.format(quote_plus(user)))
    except (http.HTTPError, http.URLError) as e:
        return "Could not fetch ban data from the Fishbans API: {}".format(e)

    if not request["success"]:
        return "Could not fetch ban data for {}.".format(user)

    user_url = "http://fishbans.com/u/{}/".format(user)
    services = request["stats"]["service"]

    out = []
    for service, ban_count in services.items():
        if ban_count != 0:
            out.append("{}: \x02{}\x02".format(service, ban_count))
        else:
            pass

    if not out:
        return "The user \x02{}\x02 has no bans.".format(user)
    else:
        return "Bans for \x02{}\x02: ".format(user) + ", ".join(out) + ". More info " \
               "at {}".format(user_url)
