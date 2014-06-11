import json

from cloudbot import hook, http
from enum import Enum

NAME_URL = "https://account.minecraft.net/buy/frame/checkName/{}"
PAID_URL = "http://www.minecraft.net/haspaid.jsp"


# enums - "because I can"
NameStatus = Enum('free', 'taken', 'invalid')


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
        return NameStatus.free
    elif "TAKEN" in response:
        return NameStatus.taken
    elif "invalid characters" in response:
        return NameStatus.invalid


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
            post_data=json.dumps(request).encode('utf-8'),
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
        # if you see this, panic
        return "The account \x02{}\x02 does not exist.".format(user)
