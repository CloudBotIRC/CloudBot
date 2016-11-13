import urllib.parse
import requests

from cloudbot import hook
from cloudbot.util import web

api_url = "https://validator.w3.org/check"

@hook.command("validate", "w3c")
def validate(text):
    """validate <url> -- Runs url through the W3C Markup Validator."""
    warning_count = 0
    error_count = 0

    text = text.strip()

    if not urllib.parse.urlparse(text).scheme:
        text = "http://" + text

    url = api_url + '?uri=' + text
    url = web.try_shorten(url)

    params = {'uri': text, 'output': 'json'}
    request = requests.get(api_url, params=params)

    if request.status_code != requests.codes.ok:
        return "Failed to fetch info: {}".format(request.status_code)

    response = request.json()
    response = response['messages']

    for mess in response:
        if mess.get("subType", None) == "warning": warning_count += 1
        if mess.get("type", None) == "error": error_count += 1

    out_warning = "warnings" if warning_count > 1 else "warning"
    out_error = "errors" if error_count > 1 else "error"

    out = "{} has {} {} and {} {} ({})".format(text, warning_count, out_warning, error_count, out_error, url)

    return out
