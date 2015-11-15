import re

import requests

from cloudbot import hook
from cloudbot.util import web


gateway = 'http://open.spotify.com/{}/{}'  # http spotify gw address
spuri = 'spotify:{}:{}'

spotify_re = re.compile(r'(spotify:(track|album|artist|user):([a-zA-Z0-9]+))', re.I)
http_re = re.compile(r'(open\.spotify\.com/(track|album|artist|user)/'
                     '([a-zA-Z0-9]+))', re.I)


@hook.command('spotify', 'sptrack')
def spotify(text):
    """spotify <song> -- Search Spotify for <song>"""
    params = {'q': text.strip()}

    request = requests.get('http://ws.spotify.com/search/1/track.json', params=params)
    if request.status_code != requests.codes.ok:
        return "Could not get track information: {}".format(request.status_code)

    data = request.json()

    try:
        _type, _id = data["tracks"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find track."
    url = web.try_shorten(gateway.format(_type, _id))

    return "\x02{}\x02 by \x02{}\x02 - {}".format(data["tracks"][0]["name"],
                                                  data["tracks"][0]["artists"][0]["name"], url)


@hook.command
def spalbum(text):
    """spalbum <album> -- Search Spotify for <album>"""
    params = {'q': text.strip()}

    request = requests.get('http://ws.spotify.com/search/1/album.json', params=params)
    if request.status_code != requests.codes.ok:
        return "Could not get album information: {}".format(request.status_code)

    data = request.json()

    try:
        _type, _id = data["albums"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find album."
    url = web.try_shorten(gateway.format(_type, _id))

    return "\x02{}\x02 by \x02{}\x02 - {}".format(data["albums"][0]["name"],
                                                  data["albums"][0]["artists"][0]["name"], url)


@hook.command
def spartist(text):
    """spartist <artist> -- Search Spotify for <artist>"""
    params = {'q': text.strip()}

    request = requests.get('http://ws.spotify.com/search/1/artist.json', params=params)
    if request.status_code != requests.codes.ok:
        return "Could not get artist information: {}".format(request.status_code)

    data = request.json()

    try:
        _type, _id = data["artists"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find artist."
    url = web.try_shorten(gateway.format(_type, _id))

    return "\x02{}\x02 - {}".format(data["artists"][0]["name"], url)


@hook.regex(http_re)
@hook.regex(spotify_re)
def spotify_url(match):
    _type = match.group(2)
    spotify_id = match.group(3)
    url = spuri.format(_type, spotify_id)
    # no error catching here, if the API is down fail silently
    params = {'uri': url}
    request = requests.get('http://ws.spotify.com/search/1/artist.json', params=params)
    if request.status_code != requests.codes.ok:
        return
    data = request.json()
    if _type == "track":
        name = data["track"]["name"]
        artist = data["track"]["artists"][0]["name"]
        album = data["track"]["album"]["name"]

        return "Spotify Track: \x02{}\x02 by \x02{}\x02 from the album \x02{}\x02".format(name, artist, album)
    elif _type == "artist":
        return "Spotify Artist: \x02{}\x02".format(data["artist"]["name"])
    elif _type == "album":
        return "Spotify Album: \x02{}\x02 - \x02{}\x02".format(data["album"]["artist"], data["album"]["name"])
