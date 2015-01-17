import re
import html
 
from cloudbot import hook
from cloudbot.util import http
 
twitch_re = re.compile(r'(.*:)//(twitch.tv|www.twitch.tv)(:[0-9]+)?(.*)', re.I)
multitwitch_re = re.compile(r'(.*:)//(www.multitwitch.tv|multitwitch.tv)/(.*)', re.I)
 
 
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
 
 
@hook.regex(multitwitch_re)
def multitwitch_url(match):
    usernames = match.group(3).split("/")
    out = ""
    for i in usernames:
        if not test(i):
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
    if not test(location):
        print("Not a valid username")
        return None
    return twitch_lookup(location)
 
 
@hook.command('twitchviewers')
@hook.command()
def twviewers(text):
    text = text.split("/")[-1]
    if test(text):
        location = text
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
    fmt = "{}: {} playing {} ({})"  # Title: nickname playing Game (x views)
    if type and id:
        if type == "b":  # I haven't found an API to retrieve broadcast info
            soup = http.get_soup("http://twitch.tv/" + location)
            title = soup.find('span', {'class': 'real_title js-title'}).text
            playing = soup.find('a', {'class': 'game js-game'}).text
            views = soup.find('span', {'id': 'views-count'}).text + " view"
            views = views + "s" if not views[0:2] == "1 " else views
            return html.unescape(fmt.format(title, channel, playing, views))
        elif type == "c":
            data = http.get_json("https://api.twitch.tv/kraken/videos/" + type + id)
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
            return h.unescape(fmt.format(title, channel, playing, viewers))
        else:
            try:
                data = http.get_json("https://api.twitch.tv/kraken/channels/" + channel)
            except:
                return "Unable to get channel data. Maybe channel is on justin.tv instead of twitch.tv?"
            title = data['status']
            playing = data['game']
            viewers = "\x034\x02Offline\x02\x0f"
            return h.unescape(fmt.format(title, channel, playing, viewers))
