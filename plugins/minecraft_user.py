import json
from util import hook, http

NAME_URL = "https://account.minecraft.net/buy/frame/checkName/{}"
PAID_URL = "http://www.minecraft.net/haspaid.jsp"


class McuError(Exception):
    pass


def get_status(name):
    """ takes a name and returns status """
    try:
        name_encoded = http.quote_plus(name)
        response = http.get(NAME_URL.format(name_encoded))
    except (http.URLError, http.HTTPError) as e:
        raise McuError("Could not get name status: {}".format(e))

    if "OK" in response:
        return "free"
    elif "TAKEN" in response:
        return "taken"
    elif "invalid characters" in response:
        return "invalid"


def get_profile(name):
    profile = {}

    # form the profile request
    request = {
        "name": name,
        "agent": "minecraft"
    }

    # submit the profile request
    try:
        headers = {"Content-Type": "application/json"}
        r = http.get_json(
            'https://api.mojang.com/profiles/page/1',
            post_data=json.dumps(request),
            headers=headers
        )
    except (http.URLError, http.HTTPError) as e:
        raise McuError("Could not get profile status: {}".format(e))

    user = r["profiles"][0]
    profile["name"] = user["name"]
    profile["id"] = user["id"]

    profile["legacy"] = user.get("legacy", False)

    try:
        response = http.get(PAID_URL, user=name)
    except (http.URLError, http.HTTPError) as e:
        raise McuError("Could not get payment status: {}".format(e))

    if "true" in response:
        profile["paid"] = True
    else:
        profile["paid"] = False

    return profile


@hook.command("haspaid")
@hook.command("mcpaid")
@hook.command
def mcuser(inp):
    """mcpaid <username> -- Gets information about the Minecraft user <account>."""
    user = inp.strip()

    try:
        # get status of name (does it exist?)
        name_status = get_status(user)
    except McuError as e:
        return e

    if name_status == "taken":
        try:
            # get information about user
            profile = get_profile(user)
        except McuError as e:
            return "Error: {}".format(e)

        profile["lt"] = ", legacy" if profile["legacy"] else ""

        if profile["paid"]:
            return u"The account \x02{name}\x02 ({id}{lt}) exists. It is a \x02paid\x02" \
                   u" account.".format(**profile)
        else:
            return u"The account \x02{name}\x02 ({id}{lt}) exists. It \x034\x02is NOT\x02\x0f a paid" \
                   u" account.".format(**profile)
    elif name_status == "free":
        return u"The account \x02{}\x02 does not exist.".format(user)
    elif name_status == "invalid":
        return u"The name \x02{}\x02 contains invalid characters.".format(user)
    else:
        # if you see this, panic
        return "Unknown Error."