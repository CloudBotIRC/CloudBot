from util import hook, http, urlnorm
import urllib
import re
import BeautifulSoup

ignored_urls = ["http://google.com","http://youtube.com"]

def parse(match):
    url = urlnorm.normalize(match.encode('utf-8'))
    if url not in ignored_urls:
        url = url.decode('utf-8')
        try:
            soup = BeautifulSoup.BeautifulSoup(http.get(url))
            return soup.title.string
        except:
            return "fail"


#@hook.regex(r'^(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~\/|\/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevel Domains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:\/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|\/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?$')
@hook.regex(r'([a-zA-Z]+://|www\.)[^ ]+')
def urlparser(match, say = None):
    url = urlnorm.normalize(match.group().encode('utf-8'))
    for x in ignored_urls:
        if x in url:
            return
    title = parse(url)
    if title == "fail":
        return
    say("(Link) %s [%s]" % (title, url))



