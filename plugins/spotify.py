import re
import time

from util import hook, http


spotify_re = (r'open\.spotify\.com\/track\/'
              '([a-z\d]{22})', re.I)

base_url = 'http://ws.spotify.com/'
api_url = base_url + 'lookup/1/.json?uri=spotify:track:{}'
track_url = "spotify://track:"


def get_video_description(spotify_id):
    request = http.get_json(api_url.format(spotify_id))

    if request.get('error'):
        return spotify_id

    data = request['track']

    out = '\x02%s\x02' % data['name']
    out += ', by %s' % data['artists']['name']
    out += ' from the album %s released in ' % data['album']['name']
    out += '%s' % data['album']['released']

    return out


@hook.regex(*spotify_re)
def spotify_url(match):
    return get_video_description(match.group(1))