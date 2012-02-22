from util import pywhois, hook

@hook.command
def whois(inp, say=None):
    try:
        w = pywhois.whois(inp)
    except:
        return "Failed to check domain info. This domain may not exist."

    print w

    domain_name = w.domain_name[0]
    expiration_date = w.expiration_date[0]
    creation_date = w.creation_date[0]
    registrant_email = w.emails[0]
    administrative_email = w.emails[1]
    say('Domain recognised! %s was registered on \x02%s\x02 and will expire on \x02%s\x02' % (domain_name, creation_date, expiration_date))
    say('Registrant email: %s Administrative email: %s' % (registrant_email, administrative_email))

