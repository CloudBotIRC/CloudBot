# Plugin by Lukeroge

from util import hook, http
from re import match
from urllib2 import urlopen, Request, HTTPError
from urllib import urlencode


class ShortenError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def bitly(url, user, apikey):
    try:
        if url[:8] == "https://":
            pass
        elif url[:7] != "http://":
            url = "http://" + url
        params = urlencode({'longUrl': url, 'login': user, 'apiKey': apikey,
                           'format': 'json'})
        j = http.get_json("http://api.bit.ly/v3/shorten?%s" % params)
        if j['status_code'] == 200:
            return j['data']['url']
        raise ShortenError('%s' % j['status_txt'])
    except (HTTPError, ShortenError):
        return "Could not shorten %s!" % url


@hook.command
def shorten(inp, bot=None):
    ".shorten <url> - Makes an j.mp/bit.ly shortlink to the url provided."
    api_user = bot.config.get("api_keys", {}).get("bitly_user", None)
    api_key = bot.config.get("api_keys", {}).get("bitly_api", None)
    if api_key is None:
        return "error: no api key set"
    return bitly(inp, api_user, api_key)
