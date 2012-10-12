""" web.py - handy functions for web services """

import http, urlnorm
import json, urllib
import yql

short_url = "http://is.gd/create.php"
paste_url = "http://paste.dmptr.com"
yql_env = "http://datatables.org/alltables.env"

YQL = yql.Public()


def query(query, params={}):
    """ runs a YQL query and returns the results """
    return YQL.execute(query, params, env=yql_env)


def isgd(url):
    """ shortens a URL with the is.gd PAI """
    url = urlnorm.normalize(url.encode('utf-8'), assume_scheme='http')
    params = urllib.urlencode({'format': 'simple', 'url': url})
    return http.get("http://is.gd/create.php?%s" % params)


def haste(text):
    """ pastes text to a hastebin server """
    page = http.get(paste_url + "/documents", post_data=text)
    data = json.loads(page)
    return("%s/%s.txt" % (paste_url, data['key']))
