""" web.py - handy functions for web services """

import http, urlnorm
import json, urllib
import yql

short_url = "http://is.gd/create.php"
paste_url = "http://paste.dmptr.com"
yql_env = "http://datatables.org/alltables.env"

YQL = yql.Public()


class ShortenError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


def isgd(url):
    """ shortens a URL with the is.gd PAI """
    url = urlnorm.normalize(url.encode('utf-8'), assume_scheme='http')
    params = urllib.urlencode({'format': 'json', 'url': url})
    request = http.get_json("http://is.gd/create.php?%s" % params)

    if "errorcode" in request:
        raise ShortenError(request["errorcode"], request["errormessage"])
    else:
        return request["shorturl"]


def haste(text):
    """ pastes text to a hastebin server """
    page = http.get(paste_url + "/documents", post_data=text)
    data = json.loads(page)
    return("%s/%s.txt" % (paste_url, data['key']))


def query(query, params={}):
    """ runs a YQL query and returns the results """
    return YQL.execute(query, params, env=yql_env)
