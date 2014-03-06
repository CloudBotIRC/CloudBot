""" web.py - handy functions for web services """

import json
import urllib.request
import urllib.parse
import urllib.error

from . import http
from . import urlnorm


short_url = "http://is.gd/create.php"
paste_url = "http://hastebin.com"


class ShortenError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


def isgd(url):
    """ shortens a URL with the is.gd API """
    url = urlnorm.normalize(url.encode('utf-8'), assume_scheme='http')
    params = urllib.parse.urlencode({'format': 'json', 'url': url})
    request = http.get_json("http://is.gd/create.php?{}".format(params))

    if "errorcode" in request:
        raise ShortenError(request["errorcode"], request["errormessage"])
    else:
        return request["shorturl"]


def try_isgd(url):
    try:
        out = isgd(url)
    except (ShortenError, http.HTTPError):
        out = url
    return out


def haste(text, ext='txt'):
    """ pastes text to a hastebin server """
    page = http.get(paste_url + "/documents", post_data=text)
    data = json.loads(page)
    return "{}/{}.{}".format(paste_url, data['key'], ext)
