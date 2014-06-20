"""
Runs a given url through the w3c validator

by Vladi
"""

from cloudbot import hook
from cloudbot.util import http


@hook.command("validate", "w3c")
def validate(text):
    """validate <url> -- Runs url through the w3c markup validator."""

    if not text.startswith('http://'):
        text = 'http://' + text

    url = 'http://validator.w3.org/check?uri=' + http.quote_plus(text)
    info = dict(http.open(url).info())

    status = info['x-w3c-validator-status'].lower()
    if status in ("valid", "invalid"):
        error_count = info['x-w3c-validator-errors']
        warning_count = info['x-w3c-validator-warnings']
        return "{} was found to be {} with {} errors and {} warnings." \
               " see: {}".format(text, status, error_count, warning_count, url)
