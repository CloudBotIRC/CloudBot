import re
import requests

from cloudbot import hook

api_url = "https://api.spotify.com/v1/search?"

spotify_re = re.compile(r'(spotify:(track|album|artist|user):([a-zA-Z0-9]+))', re.I)
http_re = re.compile(r'(open\.spotify\.com/(track|album|artist|user)/'
                     '([a-zA-Z0-9]+))', re.I)


@hook.command('spotify', 'sptrack')
def spotify(text):
    """spotify <song> -- Search Spotify for <song>"""
    params = {
        "q": text.strip(),
        "offset": 0,
        "limit": 1,
        "type": "track"
    }

    request = requests.get(api_url, params=params)
    if request.status_code != requests.codes.ok:
        return "Could not get track information: {}".format(request.status_code)

    data = request.json()["tracks"]["items"][0]

    try:
        artist, url, song, uri = (data["artists"][0]["name"],
                                  data["external_urls"]["spotify"],
                                  data["name"],
                                  data["uri"])
    except IndexError:
        return "Unable to find any tracks!"

    return "\x02{}\x02 by \x02{}\x02 - {} / {}".format(song, artist,
                                                       url, uri)


@hook.command("spalbum")
def spalbum(text):
    """spalbum <album> -- Search Spotify for <album>"""
    params = {
        "q": text.strip(),
        "offset": 0,
        "limit": 1,
        "type": "album"
    }

    request = requests.get(api_url, params=params)
    if request.status_code != requests.codes.ok:
        return "Could not get album information: {}".format(request.status_code)

    data = request.json()["albums"]["items"][0]

    try:
        artist, name, url, uri = (data["artists"][0]["name"],
                                  data["name"],
                                  data["external_urls"]["spotify"],
                                  data["uri"])

    except IndexError:
        return "Unable to find any albums!"

    return "\x02{}\x02 by \x02{}\x02 - {} / {}".format(name, artist,
                                                       url, uri)


@hook.command("spartist", "artist")
def spartist(text):
    """spartist <artist> -- Search Spotify for <artist>"""
    params = {
        "q": text.strip(),
        "offset": 0,
        "limit": 1,
        "type": "artist"
    }

    request = requests.get(api_url, params=params)
    if request.status_code != requests.codes.ok:
        return "Could not get artist information: {}".format(request.status_code)

    data = request.json()["artists"]["items"][0]

    try:
        artist, url, uri = (data["name"],
                            data["external_urls"]["spotify"],
                            data["uri"])
    except IndexError:
        return "Unable to find any artists!"

    return "\x02{}\x02 - {} / {}".format(artist, url, uri)


@hook.regex(http_re)
@hook.regex(spotify_re)
def spotify_url(match):
    _type = match.group(2)
    spotify_id = match.group(3)

    if _type == "track":
        request = requests.get("https://api.spotify.com/v1/tracks/{}".format(spotify_id))
        data = request.json()

        return "Spotify Track: \x02{}\x02 by \x02{}\x02 from the album \x02{}\x02".format(data["name"], data["album"]["artists"][0]["name"], data["album"]["name"])

    elif _type == "artist":
        request = requests.get("https://api.spotify.com/v1/artists/{}".format(spotify_id))
        data = request.json()

        return "Spotify Artist: \x02{}\x02, followers: \x02{}\x02, genres: \x02{}\x02".format(data["name"], data["followers"]["total"], ', '.join(data["genres"]))

    elif _type == "album":
        request = requests.get("https://api.spotify.com/v1/albums/{}".format(spotify_id))
        data = request.json()

        return "Spotify Album: \x02{}\x02 by \x02{}\x02".format(data["name"], data["artists"][0]["name"])
