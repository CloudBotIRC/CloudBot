import requests
import re
from bs4 import BeautifulSoup
from contextlib import closing
from cloudbot import hook

# This will match ANY we url including youtube, reddit, twitch, etc... Some additional work needs to go into
# not sending the web request etc if the match also matches an existing web regex.
blacklist = re.compile('.*(reddit\.com|redd.it|youtube.com|youtu.be|spotify.com|twitter.com|twitch.tv|amazon.co|amzn.com|steamcommunity.com|steampowered.com|newegg.com).*', re.I)
url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

opt_in = []

traditional = [
    (1024 ** 5, 'PB'),
    (1024 ** 4, 'TB'), 
    (1024 ** 3, 'GB'), 
    (1024 ** 2, 'MB'), 
    (1024 ** 1, 'KB'),
    (1024 ** 0, 'B'),
    ]


def bytesto(bytes, system = traditional):
    """ converts bytes to something """
    bytes = int(bytes)
    for factor, suffix in system:
        if bytes >= factor:
            break
    amount = int(bytes/factor)
    return str(amount) + suffix

@hook.regex(url_re)
def print_url_title(match, chan):
    if chan not in opt_in:
        return
    if re.search(blacklist, match.group()):
        return
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'
    }
    with closing(requests.get(match.group(), headers = HEADERS, stream = True)) as r:
        if not r.encoding:
            content = r.headers['content-type']
            size = bytesto(r.headers['content-length'])
            out = "Content Type: \x02{}\x02 Size: \x02{}\x02".format(content, size)
            return out
        html = BeautifulSoup(r.text)
        title = html.title.text.strip()
        out = "Title: \x02{}\x02".format(title)
        return out
