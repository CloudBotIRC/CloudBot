from util import hook, http
from urllib import quote_plus
import json

api_url = "http://www.fishbans.com/api/stats/%s/force/"


@hook.command("bans")
@hook.command
def fishbans(inp):
    "fishbans <user> -- Gets information on <user>s minecraft bans from fishbans"
    user = inp
    request = http.get_json(api_url % quote_plus(user))

    if request["success"] == False:
        return "Could not fetch ban data for %s." % user

    user_url = "http://fishbans.com/u/%s" % user
    ban_count = request["stats"]["totalbans"]

    return "The user \x02%s\x02 has \x02%s\x02 ban(s). See detailed info " \
           "at %s" % (user, ban_count, user_url)


@hook.command
def bancount(inp):
    "bancount <user> -- Gets a count of <user>s minecraft bans from fishbans"
    user = inp
    request = http.get_json(api_url % quote_plus(user))

    if request["success"] == False:
        return "Could not fetch ban data for %s." % user

    user_url = "http://fishbans.com/u/%s" % user
    services = request["stats"]["service"]

    out = []
    for service, ban_count in services.items():
        if ban_count != 0:
            out.append("%s: \x02%s\x02" % (service, ban_count))
        else:
            pass

    if not out:
        return "The user \x02%s\x02 has no bans." % user
    else:
        text = "Bans for \x02%s\x02: " % user
        return text + ", ".join(out)