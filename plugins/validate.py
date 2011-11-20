'''
Runs a given url through the w3c validator

by Vladi
'''

from util import hook, http


@hook.command
def validate(inp):
    ".validate <url> -- runs url through w3c markup validator"

    if not inp.startswith('http://'):
        inp = 'http://' + inp

    url = 'http://validator.w3.org/check?uri=' + http.quote_plus(inp)
    info = dict(http.open(url).info())

    status = info['x-w3c-validator-status'].lower()
    if status in ("valid", "invalid"):
        errorcount = info['x-w3c-validator-errors']
        warningcount = info['x-w3c-validator-warnings']
        return "%s was found to be %s with %s errors and %s warnings." \
                " see: %s" % (inp, status, errorcount, warningcount, url)
