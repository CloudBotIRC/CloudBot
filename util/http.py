# convenience wrapper for urllib2 & friends

import cookielib
import json
import urllib
import urllib2
import urlparse

from urllib import quote, quote_plus as _quote_plus

from lxml import etree, html
from bs4 import BeautifulSoup

# used in plugins that import this
from urllib2 import URLError, HTTPError

ua_cloudbot = 'Cloudbot/DEV http://github.com/CloudDev/CloudBot'

ua_firefox = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/17.0' \
             ' Firefox/17.0'
ua_old_firefox = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; ' \
                 'rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6'
ua_internetexplorer = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
ua_chrome = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, ' \
            'like Gecko) Chrome/22.0.1229.79 Safari/537.4'

jar = cookielib.CookieJar()


def get(*args, **kwargs):
    return open(*args, **kwargs).read()


def get_url(*args, **kwargs):
    return open(*args, **kwargs).geturl()


def get_html(*args, **kwargs):
    return html.fromstring(get(*args, **kwargs))


def get_soup(*args, **kwargs):
    return BeautifulSoup(get(*args, **kwargs), 'lxml')


def get_xml(*args, **kwargs):
    return etree.fromstring(get(*args, **kwargs))


def get_json(*args, **kwargs):
    return json.loads(get(*args, **kwargs))


def open(url, query_params=None, user_agent=None, post_data=None,
         referer=None, get_method=None, cookies=False, timeout=None, headers=None, **kwargs):
    if query_params is None:
        query_params = {}

    if user_agent is None:
        user_agent = ua_cloudbot

    query_params.update(kwargs)

    url = prepare_url(url, query_params)

    request = urllib2.Request(url, post_data)

    if get_method is not None:
        request.get_method = lambda: get_method

    if headers is not None:
        for header_key, header_value in headers.iteritems():
            request.add_header(header_key, header_value)

    request.add_header('User-Agent', user_agent)

    if referer is not None:
        request.add_header('Referer', referer)

    if cookies:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    else:
        opener = urllib2.build_opener()

    if timeout:
        return opener.open(request, timeout=timeout)
    else:
        return opener.open(request)


def prepare_url(url, queries):
    if queries:
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)

        query = dict(urlparse.parse_qsl(query))
        query.update(queries)
        query = urllib.urlencode(dict((to_utf8(key), to_utf8(value))
                                      for key, value in query.iteritems()))

        url = urlparse.urlunsplit((scheme, netloc, path, query, fragment))

    return url


def to_utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf8', 'ignore')
    else:
        return str(s)


def quote_plus(s):
    return _quote_plus(to_utf8(s))


def unescape(s):
    if not s.strip():
        return s
    return html.fromstring(s).text_content()
