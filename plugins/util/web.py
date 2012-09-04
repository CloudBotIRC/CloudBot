""" web.py - handy functions for web services """

import http, urlnorm
import json, urllib, urllib2

short_url = "http://is.gd/create.php"
paste_url = "http://paste.dmptr.com"


def isgd(url):
    """ shortens a URL with the is.gd PAI """
    url = urlnorm.normalize(url.encode('utf-8'))
    params = urllib.urlencode({'format': 'simple', 'url': url})
    return http.get("http://is.gd/create.php?%s" % params)


def haste(text):
    """ pastes text to a hastebin server """
    request = urllib2.Request(paste_url + "/documents", text)
    response = urllib2.urlopen(request)
    data = json.loads(response.read())
    return("%s/%s.txt" % (paste_url, data['key']))
