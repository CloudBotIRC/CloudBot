"""
Runs a given url through the w3c validator

by Vladi
"""

from util import hook, http


@hook.command('w3c')
@hook.command
def validate(inp):
    """validate <url> -- Runs url through the w3c markup validator."""

    if not inp.startswith('http://'):
        inp = 'http://' + inp

    url = 'http://validator.w3.org/check?uri=' + http.quote_plus(inp)
    info = dict(http.open(url).info())

    status = info['x-w3c-validator-status'].lower()
    if status in ("valid", "invalid"):
        errorcount = info['x-w3c-validator-errors']
        warningcount = info['x-w3c-validator-warnings']
        return "{} was found to be {} with {} errors and {} warnings." \
                " see: {}".format(inp, status, errorcount, warningcount, url)
