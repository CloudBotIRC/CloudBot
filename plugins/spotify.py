import re

from util import hook, http

gateway =  'http://open.spotify.com/{}/{}'  # http spotify gw address
spuri   =  'spotify:{}:{}'

spotify_re = (r'(spotify:(track|album|artist|user):([a-zA-Z0-9]+))', re.I)
http_re = (r'(open\.spotify\.com\/(track|album|artist|user)\/'
              '([a-zA-Z0-9]+))', re.I)

@hook.command
def spotify(inp):
    "spotify <song> -- Search Spotify for <song>"
    data = http.get_json("http://ws.spotify.com/search/1/track.json", q=inp.strip())
    try:
        type, id = data["tracks"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find track."
    url = gateway.format(type, id)
    return u"{} by {} - {}".format(data["tracks"][0]["name"], data["tracks"][0]["artists"][0]["name"], url)


@hook.regex(*http_re)
@hook.regex(*spotify_re)
def spotify_url(match):
    type = match.group(2)
    spotify_id = match.group(3)
    url = spuri.format(type, spotify_id)
    data = http.get_json("http://ws.spotify.com/lookup/1/.json", uri=url)
    if type == "track":
        name = data["track"]["name"]
        artist = data["track"]["artists"][0]["name"]
        album = data["track"]["album"]["name"]
        return u"Spotify Track: {} by {} from the album {}".format(name, artist, album) // shortened
    elif type == "artist":
        return u"Spotify Artist: {}".format(data["artist"]["name"])
    elif type == "album":
        return u"Spotify Album: {} - {}".format(data["album"]["artist"], data["album"]["name"])
