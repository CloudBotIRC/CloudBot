import urllib
import urllib.parse
import json
import re

oauth = None  # import oauth2 as oauth

from cloudbot import hook


def getdata(inp, types, api_key, api_secret):
    consumer = oauth.Consumer(api_key, api_secret)
    client = oauth.Client(consumer)
    response = client.request('http://api.rdio.com/1/', 'POST',
                              urllib.parse.urlencode({'method': 'search', 'query': inp, 'types': types, 'count': '1'}))
    data = json.loads(response[1])
    return data


@hook.command()
def rdio(text, bot):
    """<query> - searches rdio for <query>"""
    api_key = bot.config.get("api_keys", {}).get("rdio_key")
    api_secret = bot.config.get("api_keys", {}).get("rdio_secret")
    if not api_key:
        return "error: no api key set"
    data = getdata(text, "Track,Album,Artist", api_key, api_secret)
    try:
        info = data['result']['results'][0]
    except IndexError:
        return "No results."
    if 'name' in info:
        if 'artist' in info and 'album' in info:  # Track
            name = info['name']
            artist = info['artist']
            album = info['album']
            url = info['shortUrl']
            return "\x02{}\x02 by \x02{}\x02 - {} {}".format(name, artist, album, url)
        elif 'artist' in info and not 'album' in info:  # Album
            name = info['name']
            artist = info['artist']
            url = info['shortUrl']
            return "\x02{}\x02 by \x02{}\x02 - {}".format(name, artist, url)
        else:  # Artist
            name = info['name']
            url = info['shortUrl']
            return "\x02{}\x02 - {}".format(name, url)


@hook.command()
def rdiot(text, bot):
    """<query> - searches rdio for tracks matching <query>"""
    api_key = bot.config.get("api_keys", {}).get("rdio_key")
    api_secret = bot.config.get("api_keys", {}).get("rdio_secret")
    if not api_key:
        return "error: no api key set"
    data = getdata(text, "Track", api_key, api_secret)
    try:
        info = data['result']['results'][0]
    except IndexError:
        return "No results."
    name = info['name']
    artist = info['artist']
    album = info['album']
    url = info['shortUrl']
    return "\x02{}\x02 by \x02{}\x02 - {} - {}".format(name, artist, album, url)


@hook.command()
def rdioar(text, bot):
    """<query> - searches rdio for artists matching <query>"""
    api_key = bot.config.get("api_keys", {}).get("rdio_key")
    api_secret = bot.config.get("api_keys", {}).get("rdio_secret")
    if not api_key:
        return "error: no api key set"
    data = getdata(text, "Artist", api_key, api_secret)
    try:
        info = data['result']['results'][0]
    except IndexError:
        return "No results."
    name = info['name']
    url = info['shortUrl']
    return "\x02{}\x02 - {}".format(name, url)


@hook.command()
def rdioal(text, bot):
    """<query> - searches rdio for albums matching <query>"""
    api_key = bot.config.get("api_keys", {}).get("rdio_key")
    api_secret = bot.config.get("api_keys", {}).get("rdio_secret")
    if not api_key:
        return "error: no api key set"
    data = getdata(text, "Album", api_key, api_secret)
    try:
        info = data['result']['results'][0]
    except IndexError:
        return "No results."
    name = info['name']
    artist = info['artist']
    url = info['shortUrl']
    return "\x02{}\x02 by \x02{}\x02 - {}".format(name, artist, url)


rdio_re = re.compile(r'(.*:)//(rd.io|www.rdio.com|rdio.com)(:[0-9]+)?(.*)', re.I)


@hook.regex(rdio_re)
def rdio_url(match, bot):
    api_key = bot.config.get("api_keys", {}).get("rdio_key")
    api_secret = bot.config.get("api_keys", {}).get("rdio_secret")
    if not api_key:
        return None
    url = match.group(1) + "//" + match.group(2) + match.group(4)
    consumer = oauth.Consumer(api_key, api_secret)
    client = oauth.Client(consumer)
    response = client.request('http://api.rdio.com/1/', 'POST',
                              urllib.parse.urlencode({'method': 'getObjectFromUrl', 'url': url}))
    data = json.loads(response[1])
    info = data['result']
    if 'name' in info:
        if 'artist' in info and 'album' in info:  # Track
            name = info['name']
            artist = info['artist']
            album = info['album']
            return "Rdio track: \x02{}\x02 by \x02{}\x02 - {}".format(name, artist, album)
        elif 'artist' in info and not 'album' in info:  # Album
            name = info['name']
            artist = info['artist']
            return "Rdio album: \x02{}\x02 by \x02{}\x02".format(name, artist)
        else:  # Artist
            name = info['name']
            return "Rdio artist: \x02{}\x02".format(name)
