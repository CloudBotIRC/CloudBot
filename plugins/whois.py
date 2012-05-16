from util import pywhois, hook


@hook.command
def whois(inp, say=None):
    "whois <domain> -- Look up ownership infomation for <domain>"
    try:
        w = pywhois.whois(inp)
    except:
        return "Failed to check domain info. This domain may not exist."

    print w

    try:
        domain_name = w.domain_name[0]
    except IndexError, e:
        domain_name = "None"

    try:
        expiration_date = w.expiration_date[0]
    except IndexError, e:
        expiration_date = "None"

    try:
        creation_date = w.creation_date[0]
    except IndexError, e:
        creation_date = "None"

    try:
        registrant_email = w.emails[0]
    except:
        registrant_email = "None"

    try:
        administrative_email = w.emails[1]
    except:
        administrative_email = "None"

    say("Domain recognised! %s was registered on \x02%s\x02 and will "\
        "expire on \x02%s\x02" % (domain_name, creation_date, expiration_date))
    say("Registrant email: %s "\
        "Administrative email: %s" % (registrant_email, administrative_email))
