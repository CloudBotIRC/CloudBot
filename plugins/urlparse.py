from util import hook, http, urlnorm
import urllib
from urllib2 import urlopen, Request, HTTPError
import re
import BeautifulSoup

ignored_urls = ["http://google.com", "http://youtube.com",
                "http://pastebin.com", "http://mibpaste.com",
                "http://fpaste.com", "http://git.io"]

def parse(match):
    url = urlnorm.normalize(match.encode('utf-8'))
    if url not in ignored_urls:
        url = url.decode('utf-8')
        try:
            soup = BeautifulSoup.BeautifulSoup(http.get(url))
            return soup.title.string
        except:
            return "fail"

# there should be " after the ' in the regex string but I was unable to escape it properly
@hook.regex(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'.,<>?«»“”‘’]))")
def urlparser(match, say=None, bot=None):
    try:
        enabled = bot.config["plugins"]["urlparse"]["enabled"]
    except KeyError:
        enabled = False

    if not enabled:
        return

    url = urlnorm.normalize(match.group().encode('utf-8'))
    if url[:7] != "http://":
        if url[:8] != "https://":
            url = "http://" + url
    for x in ignored_urls:
        if x in url:
            return
    title = parse(url)
    if title == "fail":
        return
    title = http.unescape(title)
    realurl = http.get_url(url)
    if realurl == url:
        say(u"(Link) %s" % title)
        return
    else:
        say(u"(Link) %s [%s]" % (title, realurl))
        return
