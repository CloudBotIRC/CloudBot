from contextlib import suppress

import pythonwhois

from cloudbot import hook


@hook.command
def whois(text):
    """<domain> -- Does a whois query on <domain>."""
    domain = text.strip().lower()

    data = pythonwhois.get_whois(domain, normalized=True)
    info = []

    with suppress(KeyError):
        info.append("\x02Registrar\x02: {}".format(data["registrar"][0]))

    with suppress(KeyError):
        info.append("\x02Registered\x02: {}".format(data["creation_date"][0].strftime("%d-%m-%Y")))

    with suppress(KeyError):
        info.append("\x02Expires\x02: {}".format(data["expiration_date"][0].strftime("%d-%m-%Y")))

    info_text = ", ".join(info)
    return "{} - {}".format(domain, info_text)
