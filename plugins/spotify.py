import re
import time
import spotimeta

from util import hook, http

gateway =  'http://open.spotify.com/{}/{}'  # http spotify gw address
spotify_re = (r'(open\.spotify\.com\/(track|album|artist|user)\/'
              '([a-zA-Z0-9]+))', re.I)

@hook.regex(*spotify_re)
def spotify_url(match):
    spotify_type = match.group(2)
    print spotify_type
    spotify_id = match.group(3)
    url = gateway.format(spotify_type, spotify_id)
    data = spotimeta.lookup(url)
    if spotify_type == "track":
        return "Spotify Track: {} - {}".format(data["result"]["artist"]["name"], data["result"]["name"])
    elif spotify_type == "artist":
        return "Spotify Artist: {}".format(data["result"]["name"])
    elif spotify_type == "album":
        return "Spotify Album: {} - {}".format(data["result"]["artist"]["name"], data["result"]["name"])