""" web.py - handy functions for web services """

import http
from urllib import urlencode


class ShortenError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def bitly(url, user, api_key):
    """ shortens a URL with the bit.ly API """
    if not "://" in url:
        url = "http://" + url
    params = urlencode({'longUrl': url, 'login': user, 'apiKey': api_key,
                        'format': 'json'})
    j = http.get_json("http://api.bit.ly/v3/shorten?%s" % params)
    if j['status_code'] == 200:
        return j['data']['url']
    raise ShortenError('%s' % j['status_txt'])
