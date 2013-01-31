import re
import time
import spotimeta

from util import hook, http

spotify_re = (r'(open\.spotify\.com/(track|album|artist|user)'
              '([a-zA-Z0-9]+{22})', re.I)

gateway =  'http://ws.spotify.com/lookup/1/'  # http spotify gw address

spotify_track_res = ( re.compile(r'spotify:(?P<type>\w+):(?P<track_id>\w{22})'),
            re.compile(r'http://open.spotify.com/(?P<type>\w+)/(?P<track_id>\w{22})') )

def get_spotify_ids(s):
    for r in spotify_track_res:
        for type, track in r.findall(s):
            yield type, track

@hook.regex(*spotify_re)
def spotify_url(match):
    for type, spotify_id in get_spotify_ids(match):
        url = '%s?uri=spotify:%s:%s' %(gateway, type, spotify_id)
    track = spotimeta.lookup(url)
    out = track["result"]["artist"]["name"], "-", track["result"]["name"]
    return out
