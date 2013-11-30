"""
URI Normalization function:
 * Always provide the URI scheme in lowercase characters.
 * Always provide the host, if any, in lowercase characters.
 * Only perform percent-encoding where it is essential.
 * Always use uppercase A-through-F characters when percent-encoding.
 * Prevent dot-segments appearing in non-relative URI paths.
 * For schemes that define a default authority, use an empty authority if the
   default is desired.
 * For schemes that define an empty path to be equivalent to a path of "/",
   use "/".
 * For schemes that define a port, use an empty port if the default is desired
 * All portions of the URI must be utf-8 encoded NFC from Unicode strings

implements:
  http://gbiv.com/protocols/uri/rev-2002/rfc2396bis.html#canonical-form
  http://www.intertwingly.net/wiki/pie/PaceCanonicalIds

inspired by:
  Tony J. Ibbs,    http://starship.python.net/crew/tibs/python/tji_url.py
  Mark Nottingham, http://www.mnot.net/python/urlnorm.py
"""

__license__ = "Python"

import re
import unicodedata
import urlparse
from urllib import quote, unquote

default_port = {
    'http': 80,
}


class Normalizer(object):
    def __init__(self, regex, normalize_func):
        self.regex = regex
        self.normalize = normalize_func


normalizers = (Normalizer(re.compile(
    r'(?:https?://)?(?:[a-zA-Z0-9\-]+\.)?(?:amazon|amzn){1}\.(?P<tld>[a-zA-Z\.]{2,})\/(gp/(?:product|offer-listing|customer-media/product-gallery)/|exec/obidos/tg/detail/-/|o/ASIN/|dp/|(?:[A-Za-z0-9\-]+)/dp/)?(?P<ASIN>[0-9A-Za-z]{10})'),
                          lambda m: r'http://amazon.%s/dp/%s' % (m.group('tld'), m.group('ASIN'))),
               Normalizer(re.compile(r'.*waffleimages\.com.*/([0-9a-fA-F]{40})'),
                          lambda m: r'http://img.waffleimages.com/%s' % m.group(1)),
               Normalizer(re.compile(r'(?:youtube.*?(?:v=|/v/)|youtu\.be/|yooouuutuuube.*?id=)([-_a-zA-Z0-9]+)'),
                          lambda m: r'http://youtube.com/watch?v=%s' % m.group(1)),
)


def normalize(url, assume_scheme=False):
    """Normalize a URL."""

    scheme, auth, path, query, fragment = urlparse.urlsplit(url.strip())
    userinfo, host, port = re.search('([^@]*@)?([^:]*):?(.*)', auth).groups()

    # Always provide the URI scheme in lowercase characters.
    scheme = scheme.lower()

    # Always provide the host, if any, in lowercase characters.
    host = host.lower()
    if host and host[-1] == '.':
        host = host[:-1]
    if host and host.startswith("www."):
        if not scheme:
            scheme = "http"
        host = host[4:]
    elif path and path.startswith("www."):
        if not scheme:
            scheme = "http"
        path = path[4:]

    if assume_scheme and not scheme:
        scheme = assume_scheme.lower()

    # Only perform percent-encoding where it is essential.
    # Always use uppercase A-through-F characters when percent-encoding.
    # All portions of the URI must be utf-8 encoded NFC from Unicode strings
    def clean(string):
        string = unicode(unquote(string), 'utf-8', 'replace')
        return unicodedata.normalize('NFC', string).encode('utf-8')

    path = quote(clean(path), "~:/?#[]@!$&'()*+,;=")
    fragment = quote(clean(fragment), "~")

    # note care must be taken to only encode & and = characters as values
    query = "&".join(["=".join([quote(clean(t), "~:/?#[]@!$'()*+,;=")
                                for t in q.split("=", 1)]) for q in query.split("&")])

    # Prevent dot-segments appearing in non-relative URI paths.
    if scheme in ["", "http", "https", "ftp", "file"]:
        output = []
        for input in path.split('/'):
            if input == "":
                if not output:
                    output.append(input)
            elif input == ".":
                pass
            elif input == "..":
                if len(output) > 1:
                    output.pop()
            else:
                output.append(input)
        if input in ["", ".", ".."]:
            output.append("")
        path = '/'.join(output)

    # For schemes that define a default authority, use an empty authority if
    # the default is desired.
    if userinfo in ["@", ":@"]:
        userinfo = ""

    # For schemes that define an empty path to be equivalent to a path of "/",
    # use "/".
    if path == "" and scheme in ["http", "https", "ftp", "file"]:
        path = "/"

    # For schemes that define a port, use an empty port if the default is
    # desired
    if port and scheme in default_port.keys():
        if port.isdigit():
            port = str(int(port))
            if int(port) == default_port[scheme]:
                port = ''

    # Put it all back together again
    auth = (userinfo or "") + host
    if port:
        auth += ":" + port
    if url.endswith("#") and query == "" and fragment == "":
        path += "#"
    normal_url = urlparse.urlunsplit((scheme, auth, path, query,
                                      fragment)).replace("http:///", "http://")
    for norm in normalizers:
        m = norm.regex.match(normal_url)
        if m:
            return norm.normalize(m)
    return normal_url
