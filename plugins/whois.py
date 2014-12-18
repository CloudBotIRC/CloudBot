import pythonwhois

from pprint import pprint

from cloudbot import hook

@hook.command
def whois(text):
    domain = text.strip().lower()

    whois = pythonwhois.get_whois(domain, normalized=True)

    info = []

    try:
        i = "\x02Registrar\x02: {}".format(whois["registrar"][0])
        info.append(i)
    except:
        pass

    try:
        i = "\x02Registered\x02: {}".format(whois["creation_date"][0].strftime("%Y-%m-%d"))
        info.append(i)
    except:
        pass


    try:
        i = "\x02Expires\x02: {}".format(whois["expiration_date"][0].strftime("%Y-%m-%d"))
        info.append(i)
    except:
        pass



    pprint(whois)


    info_text = ", ".join(info)
    return "{} - {}".format(domain, info_text)
