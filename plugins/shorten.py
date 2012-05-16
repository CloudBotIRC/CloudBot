# Plugin by Lukeroge

from util import hook
from urllib2 import HTTPError
from util.web import bitly, ShortenError


@hook.command
def shorten(inp, bot=None):
    "shorten <url> - Makes an j.mp/bit.ly shortlink to the url provided."
    api_user = bot.config.get("api_keys", {}).get("bitly_user", None)
    api_key = bot.config.get("api_keys", {}).get("bitly_api", None)
    if api_key is None:
        return "error: no api key set"

    try:
        return bitly(inp, api_user, api_key)
    except (HTTPError, ShortenError):
        return "Could not shorten '%s'!" % inp
