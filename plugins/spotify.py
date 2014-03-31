import re
from urllib import urlencode

from util import hook, http, web

gateway = 'http://open.spotify.com/{}/{}'  # http spotify gw address
spuri = 'spotify:{}:{}'

spotify_re = (r'(spotify:(track|album|artist|user):([a-zA-Z0-9]+))', re.I)
http_re = (r'(open\.spotify\.com\/(track|album|artist|user)\/'
           '([a-zA-Z0-9]+))', re.I)


def sptfy(inp, sptfy=False):
    if sptfy:
        shortenurl = "http://sptfy.com/index.php"
        data = urlencode({'longUrl': inp, 'shortUrlDomain': 1, 'submitted': 1, "shortUrlFolder": 6, "customUrl": "",
                          "shortUrlPassword": "", "shortUrlExpiryDate": "", "shortUrlUses": 0, "shortUrlType": 0})
        try:
            soup = http.get_soup(shortenurl, post_data=data, cookies=True)
        except:
            return inp
        try:
            link = soup.find('div', {'class': 'resultLink'}).text.strip()
            return link
        except:
            message = "Unable to shorten URL: %s" % \
                      soup.find('div', {'class': 'messagebox_text'}).find('p').text.split("<br/>")[0]
            return message
    else:
        return web.try_isgd(inp)


@hook.command('sptrack')
@hook.command
def spotify(inp):
    """spotify <song> -- Search Spotify for <song>"""
    try:
        data = http.get_json("http://ws.spotify.com/search/1/track.json", q=inp.strip())
    except Exception as e:
        return "Could not get track information: {}".format(e)

    try:
        type, id = data["tracks"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find track."
    url = sptfy(gateway.format(type, id))
    return u"\x02{}\x02 by \x02{}\x02 - {}".format(data["tracks"][0]["name"],
                                                           data["tracks"][0]["artists"][0]["name"], url)


@hook.command
def spalbum(inp):
    """spalbum <album> -- Search Spotify for <album>"""
    try:
        data = http.get_json("http://ws.spotify.com/search/1/album.json", q=inp.strip())
    except Exception as e:
        return "Could not get album information: {}".format(e)

    try:
        type, id = data["albums"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find album."
    url = sptfy(gateway.format(type, id))
    return u"\x02{}\x02 by \x02{}\x02 - {}".format(data["albums"][0]["name"],
                                                           data["albums"][0]["artists"][0]["name"], url)


@hook.command
def spartist(inp):
    """spartist <artist> -- Search Spotify for <artist>"""
    try:
        data = http.get_json("http://ws.spotify.com/search/1/artist.json", q=inp.strip())
    except Exception as e:
        return "Could not get artist information: {}".format(e)

    try:
        type, id = data["artists"][0]["href"].split(":")[1:]
    except IndexError:
        return "Could not find artist."
    url = sptfy(gateway.format(type, id))
    return u"\x02{}\x02 - {}".format(data["artists"][0]["name"], url)


@hook.regex(*http_re)
@hook.regex(*spotify_re)
def spotify_url(match):
    type = match.group(2)
    spotify_id = match.group(3)
    url = spuri.format(type, spotify_id)
    # no error catching here, if the API is down fail silently
    data = http.get_json("http://ws.spotify.com/lookup/1/.json", uri=url)
    if type == "track":
        name = data["track"]["name"]
        artist = data["track"]["artists"][0]["name"]
        album = data["track"]["album"]["name"]
        return u"Spotify Track: \x02{}\x02 by \x02{}\x02 from the album \x02{}\x02 - {}".format(name, artist,
                                                                                                        album, sptfy(
                gateway.format(type, spotify_id)))
    elif type == "artist":
        return u"Spotify Artist: \x02{}\x02 - {}".format(data["artist"]["name"],
                                                                 sptfy(gateway.format(type, spotify_id)))
    elif type == "album":
        return u"Spotify Album: \x02{}\x02 - \x02{}\x02 - {}".format(data["album"]["artist"],
                                                                             data["album"]["name"],
                                                                             sptfy(gateway.format(type, spotify_id)))
