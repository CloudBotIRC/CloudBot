import pythonwhois

from cloudbot import hook


@hook.command
def whois(text):
    domain = text.strip().lower()

    data = pythonwhois.get_whois(domain, normalized=True)

    info = []

    try:
        i = "\x02Registrar\x02: {}".format(data["registrar"][0])
        info.append(i)
    except:
        pass

    try:
        i = "\x02Registered\x02: {}".format(data["creation_date"][0].strftime("%d-%m-%Y"))
        info.append(i)
    except:
        pass

    try:
        i = "\x02Expires\x02: {}".format(data["expiration_date"][0].strftime("%d-%m-%Y"))
        info.append(i)
    except:
        pass

    info_text = ", ".join(info)
    return "{} - {}".format(domain, info_text)
