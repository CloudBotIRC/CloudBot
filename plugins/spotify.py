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
    spotify_id = match.group(3)
    url = gateway.format(spotify_type, spotify_id)
    track = spotimeta.lookup(url)
    return "{} - {}".format(track["result"]["artist"]["name"], track["result"]["name"])