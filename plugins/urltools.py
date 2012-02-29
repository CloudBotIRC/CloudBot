from util import hook, http, urlnorm
import urllib
from urllib2 import urlopen, Request, HTTPError
import re
import BeautifulSoup

ignored_urls = ["http://google.com", "http://youtube.com",
                "http://pastebin.com", "http://mibpaste.com",
                "http://fpaste.com", "http://git.io"]

wordDic = {
'&#34;': '"',
'&#39;': '\'',
'&#38;': '&',
'&#60;': '<',
'&#62;': '>',
'&#171;': '«',
'&quot;': '"',
'&apos;': '\'',
'&amp;': '&',
'&lt;': '<',
'&gt;': '>',
'&laquo;': '«',
'&#33;': '!',
'&#036;': '$',
'  ': ' '}


def parse(match):
    url = urlnorm.normalize(match.encode('utf-8'))
    if url not in ignored_urls:
        url = url.decode('utf-8')
        try:
            soup = BeautifulSoup.BeautifulSoup(http.get(url))
            return soup.title.string
        except:
            return "fail"


def multiwordReplace(text, wordDic):
    rc = re.compile('|'.join(map(re.escape, wordDic)))

    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)


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
    title = multiwordReplace(title, wordDic)
    realurl = http.get_url(url)
    if realurl == url:
        say("(Link) %s" % title)
        return
    else:
        say("(Link) %s [%s]" % (title, realurl))
        return
