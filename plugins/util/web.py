""" web.py - handy functions for web services """

import http, urlnorm
import json, urllib2
from urllib import urlencode


class ShortenError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# this is not used in any plugins right now
def bitly(url, user, api_key):
    """ shortens a URL with the bit.ly API """
    url = urlnorm.normalise(url)
    params = urlencode({'longUrl': url, 'login': user, 'apiKey': api_key,
                        'format': 'json'})
    j = http.get_json("http://api.bit.ly/v3/shorten?%s" % params)
    if j['status_code'] == 200:
        return j['data']['url']
    raise ShortenError('%s' % j['status_txt'])


def isgd(url):
    """ shortens a URL with the is.gd PAI """
    url = urlnorm.normalize(url.encode('utf-8'))
    params = urlencode({'format': 'simple', 'url': url})
    return http.get("http://is.gd/create.php?%s" % params)


def haste(data):
    URL = "http://paste.dmptr.com"
    request = urllib2.Request(URL + "/documents", data)
    response = urllib2.urlopen(request)
    return("%s/%s" % (URL, json.loads(response.read())['key']))