import re
import html

from cloudbot import hook
from cloudbot.util import http


twitch_re = re.compile(r'(.*:)//(twitch.tv|www.twitch.tv)(:[0-9]+)?(.*)', re.I)
multitwitch_re = re.compile(r'(.*:)//(www.multitwitch.tv|multitwitch.tv)/(.*)', re.I)


def test_name(s):
    valid = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/')
    return set(s) <= valid


def twitch_lookup(location):
    locsplit = location.split("/")
    if len(locsplit) > 1 and len(locsplit) == 3:
        channel = locsplit[0]
        _type = locsplit[1]  # should be b or c
        _id = locsplit[2]
    else:
        channel = locsplit[0]
        _type = None
        _id = None
    fmt = "{}: {} playing {} ({})"  # Title: nickname playing Game (x views)
    if _type and _id:
        if _type == "b":  # I haven't found an API to retrieve broadcast info
            soup = http.get_soup("http://twitch.tv/" + location)
            title = soup.find('span', {'class': 'real_title js-title'}).text
            playing = soup.find('a', {'class': 'game js-game'}).text
            views = soup.find('span', {'id': 'views-count'}).text + " view"
            views = views + "s" if not views[0:2] == "1 " else views
            return html.unescape(fmt.format(title, channel, playing, views))
        elif _type == "c":
            data = http.get_json("https://api.twitch.tv/kraken/videos/" + _type + _id)
            title = data['title']
            playing = data['game']
            views = str(data['views']) + " view"
            views = views + "s" if not views[0:2] == "1 " else views
            return html.unescape(fmt.format(title, channel, playing, views))
    else:
        data = http.get_json("https://api.twitch.tv/kraken/streams?channel=" + channel)
        if data["streams"]:
            title = data["streams"][0]["channel"]["status"]
            playing = data["streams"][0]["game"]
            v = data["streams"][0]["viewers"]
            viewers = "\x033\x02Online now!\x02\x0f " + str(v) + " viewer" + ("s" if v != 1 else "")
            return html.unescape(fmt.format(title, channel, playing, viewers))
        else:
            try:
                data = http.get_json("https://api.twitch.tv/kraken/channels/" + channel)
            except Exception:
                return "Unable to get channel data. Maybe channel is on justin.tv instead of twitch.tv?"
            title = data['status']
            playing = data['game']
            viewers = "\x034\x02Offline\x02\x0f"
            return html.unescape(fmt.format(title, channel, playing, viewers))


@hook.regex(multitwitch_re)
def multitwitch_url(match):
    usernames = match.group(3).split("/")
    out = ""
    for i in usernames:
        if not test_name(i):
            print("Not a valid username")
            return None
        if out == "":
            out = twitch_lookup(i)
        else:
            out = out + " \x02|\x02 " + twitch_lookup(i)
    return out


@hook.regex(twitch_re)
def twitch_url(match):
    bit = match.group(4).split("#")[0]
    location = "/".join(bit.split("/")[1:])
    if not test_name(location):
        print("Not a valid username")
        return None
    return twitch_lookup(location)


@hook.command('twitch', 'twitchtv')
def twitch(text):
    """<channel name> -- Retrieves the channel and shows its offline/offline status"""
    text = text.split("/")[-1]
    if test_name(text):
        location = text
    else:
        return "Not a valid channel name."
    return twitch_lookup(location).split("(")[-1].split(")")[0].replace("Online now! ", "")
