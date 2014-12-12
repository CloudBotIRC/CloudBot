import urllib.parse

import requests

from cloudbot import hook
from cloudbot.util import web


@hook.command("validate", "w3c")
def validate(text):
    """validate <url> -- Runs url through the w3c markup validator."""
    text = text.strip()

    if not urllib.parse.urlparse(text).scheme:
        text = "http://" + text

    params = {'uri': text}
    request = requests.get('http://validator.w3.org/check', params=params)

    info = request.headers
    url = web.try_shorten(request.url)

    status = info['x-w3c-validator-status'].lower()
    print(status)
    if status in ("valid", "invalid"):
        error_count = info['x-w3c-validator-errors']
        warning_count = info['x-w3c-validator-warnings']
        return "{} was found to be {} with {} error{} and {} warning{}" \
               " - {}".format(text, status, error_count, "s"[error_count == 1:], warning_count,
                              "s"[warning_count == 1:], url)
    elif status == "abort":
        return "Invalid input."
