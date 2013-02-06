import re
import spotimeta

from util import hook, http

gateway =  'http://open.spotify.com/{}/{}'  # http spotify gw address

spotify_re = (r'(spotify:(track|album|artist|user):([a-zA-Z0-9]+))', re.I)
http_re = (r'(open\.spotify\.com\/(track|album|artist|user)\/'
              '([a-zA-Z0-9]+))', re.I)

@hook.command
def spotify(inp):
    "spotify <song> -- Search Spotify for <song>"
    data = spotimeta.search_track(inp.strip())
    try:
        type, id = data["result"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find track."
    url = gateway.format(type, id)
    return u"{} by {} - {}".format(data["result"][0]["name"], data["result"][0]["artist"]["name"], url)


@hook.regex(*http_re)
@hook.regex(*spotify_re)
def spotify_url(match):
    type = match.group(2)
    spotify_id = match.group(3)
    url = gateway.format(type, spotify_id)
    data = spotimeta.lookup(url)
    if type == "track":
        return u"Spotify Track: {} by {} from the album {}".format(data["result"]["name"], data["result"]["artist"]["name"], data["result"]["album"]["name"])
    elif type == "artist":
        return u"Spotify Artist: {}".format(data["result"]["name"])
    elif type == "album":
        return u"Spotify Album: {} - {}".format(data["result"]["artist"]["name"], data["result"]["name"])