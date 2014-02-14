import re
from HTMLParser import HTMLParser

from util import hook, http


twitch_re = (r'(.*:)//(twitch.tv|www.twitch.tv)(:[0-9]+)?(.*)', re.I)
multitwitch_re = (r'(.*:)//(www.multitwitch.tv|multitwitch.tv)/(.*)', re.I)


def test(s):
    valid = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_/')
    return set(s) <= valid


def truncate(msg):
    nmsg = msg.split(" ")
    out = None
    x = 0
    for i in nmsg:
        if x <= 7:
            if out:
                out = out + " " + nmsg[x]
            else:
                out = nmsg[x]
        x += 1
    if x <= 7:
        return out
    else:
        return out + "..."


@hook.regex(*multitwitch_re)
def multitwitch_url(match):
    usernames = match.group(3).split("/")
    out = ""
    for i in usernames:
        if not test(i):
            print "Not a valid username"
            return None
        if out == "":
            out = twitch_lookup(i)
        else:
            out = out + " \x02|\x02 " + twitch_lookup(i)
    return out


@hook.regex(*twitch_re)
def twitch_url(match):
    bit = match.group(4).split("#")[0]
    location = "/".join(bit.split("/")[1:])
    if not test(location):
        print "Not a valid username"
        return None
    return twitch_lookup(location)


@hook.command('twitchviewers')
@hook.command
def twviewers(inp):
    inp = inp.split("/")[-1]
    if test(inp):
        location = inp
    else:
        return "Not a valid channel name."
    return twitch_lookup(location).split("(")[-1].split(")")[0].replace("Online now! ", "")


def twitch_lookup(location):
    locsplit = location.split("/")
    if len(locsplit) > 1 and len(locsplit) == 3:
        channel = locsplit[0]
        type = locsplit[1]  # should be b or c
        id = locsplit[2]
    else:
        channel = locsplit[0]
        type = None
        id = None
    h = HTMLParser()
    fmt = "{}: {} playing {} ({})"  # Title: nickname playing Game (x views)
    if type and id:
        if type == "b":  # I haven't found an API to retrieve broadcast info
            soup = http.get_soup("http://twitch.tv/" + location)
            title = soup.find('span', {'class': 'real_title js-title'}).text
            playing = soup.find('a', {'class': 'game js-game'}).text
            views = soup.find('span', {'id': 'views-count'}).text + " view"
            views = views + "s" if not views[0:2] == "1 " else views
            return h.unescape(fmt.format(title, channel, playing, views))
        elif type == "c":
            data = http.get_json("https://api.twitch.tv/kraken/videos/" + type + id)
            title = data['title']
            playing = data['game']
            views = str(data['views']) + " view"
            views = views + "s" if not views[0:2] == "1 " else views
            return h.unescape(fmt.format(title, channel, playing, views))
    else:
        data = http.get_json("http://api.justin.tv/api/stream/list.json?channel=" + channel)
        if data and len(data) >= 1:
            data = data[0]
            title = data['title']
            playing = data['meta_game']
            viewers = "\x033\x02Online now!\x02\x0f " + str(data["channel_count"]) + " viewer"
            print viewers
            viewers = viewers + "s" if not " 1 view" in viewers else viewers
            print viewers
            return h.unescape(fmt.format(title, channel, playing, viewers))
        else:
            try:
                data = http.get_json("https://api.twitch.tv/kraken/channels/" + channel)
            except:
                return
            title = data['status']
            playing = data['game']
            viewers = "\x034\x02Offline\x02\x0f"
            return h.unescape(fmt.format(title, channel, playing, viewers))
