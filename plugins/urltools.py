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

@hook.regex(r'([a-zA-Z]://|www\.)?[^ ]+(\.[a-z]+)+')
def urlparser(match, say=None):
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
        say("(Link) %s" % title)
        return
    else:
        say("(Link) %s [%s]" % (title, realurl))
        return
