from util import pywhois, hook

@hook.command
def whois(inp, say=None):
    try:
        w = pywhois.whois(inp)
    except:
        return "Failed to check domain info. This domain may not exist."

    print w

    try:
        domain_name = w.domain_name[0]
    except IndexError, e:
        domain_name="none."

    try:
        expiration_date = w.expiration_date[0]
    except IndexError, e:
        expiration_date="none."

    try:
        creation_date = w.creation_date[0]
    except IndexError, e:
        creation_date="none."

    try:
        registrant_email = w.emails[0]
    except:
        registrant_email="none."

    try:
        administrative_email = w.emails[1]
    except:
        administrative_email="none."

    say('Domain recognised! %s was registered on \x02%s\x02 and will expire on \x02%s\x02' % (domain_name, creation_date, expiration_date))
    say('Registrant email: %s Administrative email: %s' % (registrant_email, administrative_email))

