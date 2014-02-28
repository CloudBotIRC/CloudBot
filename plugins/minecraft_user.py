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


def is_paid(name):
    """ takes a name and returns true if it's assosiated with a paid minecraft account
        if the account does not exist or is not paid, returns false """
    try:
        response = http.get(PAID_URL, user=name)
    except (http.URLError, http.HTTPError) as e:
        raise McuError("Could not get payment status: {}".format(e))

    if "true" in response:
        return True
    else:
        return False


@hook.command("haspaid")
@hook.command("mcpaid")
@hook.command
def mcuser(inp):
    """mcpaid <username> -- Gets information about the Minecraft user <account>."""
    user = inp.strip()

    try:
        name_status = get_status(user)
    except McuError as e:
        return e

    if name_status == "taken":
        try:
            paid = is_paid(user)
        except McuError as e:
            return e

        if paid:
            return u"The account \x02{}\x02 exists and \x02is a paid\x02 minecraft account.".format(user)
        else:
            return u"The account \x02{}\x02 exists, but \x02is not\x02 a paid minecraft account.".format(user)
    elif name_status == "free":
        return u"The account \x02{}\x02 does not exist.".format(user)
    elif name_status == "invalid":
        return u"The name \x02{}\x02 contains invalid characters.".format(user)
    else:
        # if you see this, panic
        return "Unknown Error."