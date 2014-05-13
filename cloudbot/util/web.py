""" web.py - handy functions for web services """

import json
import urllib.request
import urllib.parse
import urllib.error

from . import urlnorm, http

short_url = "http://is.gd/create.php"
paste_url = "http://hastebin.com"


class ShortenError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


def isgd(url):
    """
    Shortens a URL with the is.gd API.
    :type url: str
    :rtype: str
    """
    url = urlnorm.normalize(url, assume_scheme='http')
    params = urllib.parse.urlencode({'format': 'json', 'url': url})
    request = http.get_json("http://is.gd/create.php?{}".format(params))

    if "errorcode" in request:
        raise ShortenError(request["errorcode"], request["errormessage"])
    else:
        return request["shorturl"]


def try_isgd(url):
    """
    Attempts to shorten a URL with the is.gd API, or returns the original URL if shortening failed.
    :type url: str
    :rtype: str
    """
    try:
        out = isgd(url)
    except (ShortenError, http.HTTPError):
        out = url
    return out


def haste(text, ext='txt'):
    """
    Pastes text to a hastebin server.
    :type text: str
    :type ext: str
    :rtype: str
    """
    if isinstance(text, str):
        text = text.encode('utf-8')
    page = http.get(paste_url + "/documents", post_data=text)
    data = json.loads(page)
    return "{}/{}.{}".format(paste_url, data['key'], ext)
