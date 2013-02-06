""""Library for querying the Spotify metadata service"""

__version__ = "0.2"
__author__ = "Rune Halvorsen <runefh@gmail.com>"
__homepage__ = "http://bitbucket.org/runeh/spotimeta/"
__docformat__ = "restructuredtext"


import sys
import urllib2
import time

try:
    from email.utils import parsedate_tz, mktime_tz, formatdate
except ImportError: # utils module name was lowercased after 2.4
    from email.Utils import parsedate_tz, mktime_tz, formatdate


from urllib import urlencode
from parser import parse_lookup_doc, parse_search_doc


API_VERSION = "1"
USER_AGENT = "Spotimeta %s" % __version__


class SpotimetaError(Exception):
    """Superclass for all spotimeta exceptions. Adds no functionality. Only
    there so it's possible to set up try blocks that catch all spotimeta
    errors, regardless of class"""
    pass


class RequestTimeout(SpotimetaError):
    """Raised when the timeout flag is in use and a request did not finish
    within the allotted time."""
    pass


class NotFound(SpotimetaError):
    """Raised when doing lookup on something that does not exist. Triggered
    by the 404 http status code"""
    pass


class RateLimiting(SpotimetaError):
    """Raised when the request was not completed due to rate limiting
    restrictions"""
    pass


class ServiceUnavailable(SpotimetaError):
    """Raised when the metadata service is not available (that is, the server
    is up, but not accepting API requests at this time"""
    pass


class ServerError(SpotimetaError):
    """Raised when an internal server error occurs. According to the spotify
    documentation, this "should not happen"."""
    pass


def canonical(url_or_uri):
    """returns a spotify uri, regardless if a url or uri is passed in"""
    if url_or_uri.startswith("http"): # assume it's a url
        parts = url_or_uri.split("/")
        return "spotify:%s:%s" % (parts[-2], parts[-1])
    else:
        return url_or_uri


def entrytype(url_or_uri):
    """Return "album", "artist" or "track" based on the type of entry the uri
    or url refers to."""
    uri = canonical(url_or_uri)
    try:
        return uri.split(":")[1]
    except IndexError:
        return None


class Metadata(object):

    def __init__(self, cache=None, rate=10, timeout=None, user_agent=None):
        self.cache = cache # not implemented yet
        self.rate = rate # not implemented yet
        self.timeout = timeout
        self.user_agent = user_agent or USER_AGENT
        self._timeout_supported = True
        self._port = "80"
        self._host = "ws.spotify.com"
        self._detailtypes = {
            "artist": {1: "album", 2: "albumdetail"},
            "album": {1: "track", 2: "trackdetail"}
        }


        major, minor = sys.version_info[:2]
        if self.timeout and major == 2 and minor <6:
            self._timeout_supported = False
            import warnings
            warnings.warn("Timeouts in urllib not supported in this version" +
                          " of python. timeout argument will be ignored!")


    def _do_request(self, url, headers):
        """Perform an actual response. Deal with 200 and 304 responses
        correctly. If another error occurs, raise the appropriate
        exception"""
        try:
            req = urllib2.Request(url, None, headers)
            if self.timeout and self._timeout_supported:
                return urllib2.urlopen(req, timeout=self.timeout)
            else:
                return urllib2.urlopen(req)

        except urllib2.HTTPError, e:
            if e.code == 304:
                return e # looks wrong but isnt't. On non fatal errors the
                         # exception behaves like the retval from urlopen
            elif e.code == 404:
                raise NotFound()
            elif e.code == 403:
                raise RateLimiting()
            elif e.code == 500:
                raise ServerError()
            elif e.code == 503:
                raise ServiceUnavailable()
            else:
                raise # this should never happen
        except urllib2.URLError, e:
            """Probably timeout. should do a better check. FIXME"""
            raise RequestTimeout()
        except:
            raise
            # all the exceptions we don't know about yet. Probably
            # some socket errors will come up here.

    def _get_url(self, url, query, if_modified_since=None):
        """Perform an http requests and return the open file-like object, if
        there is one, as well as the expiry time and last-modified-time
        if they were present in the reply.
        If the if_modified_since variable is passed in, send it as the value
        of the If-Modified-Since header."""
        if query:
            url = "%s?%s" %(url, urlencode(query))

        headers = {'User-Agent': self.user_agent}
        if if_modified_since:
            headers["If-Modified-Since"] = formatdate(if_modified_since, False, True)

        fp = self._do_request(url, headers)

        # at this point we have something file like after the request
        # finished with a 200 or 304.

        headers = fp.info()
        if fp.code == 304:
            fp = None

        expires = None
        if "Expires" in headers:
            expires = mktime_tz(parsedate_tz(headers.get("Expires")))

        modified = None
        if "Last-Modified" in headers:
            modified = mktime_tz(parsedate_tz(headers.get("Last-Modified")))

        return fp, modified, expires


    def lookup(self, uri, detail=0):
        """Lookup metadata for a URI. Optionally ask for extra details.
        The details argument is an int: 0 for normal ammount of detauls, 1
        for extra details, and 2 for most details. For tracks the details
        argument is ignored, as the Spotify api only has one level of detail
        for tracks. For the meaning of the detail levels, look at the
        Spotify api docs"""

        key = "%s:%s" % (uri, detail)
        res, modified, expires = self._cache_get(key)

        if res and time.time() < expires:
            return res
        # else, cache is outdated or entry not in it. Normal request cycle

        url = "http://%s:%s/lookup/%s/" % (self._host, self._port, API_VERSION)
        uri = canonical(uri)
        query = {"uri": uri}
        kind = entrytype(uri)

        if detail in (1,2) and kind in self._detailtypes.keys():
            query["extras"] = self._detailtypes[kind][detail]

        fp, new_modified, new_expires = self._get_url(url, query, modified)

        if fp: # We got data, sweet
            res = parse_lookup_doc(fp, uri=uri)

        self._cache_put(key, res, new_modified or modified, new_expires or expires)
        return res

    def search_album(self, term, page=None):
        """The first page is numbered 1!"""
        url = "http://%s:%s/search/%s/album" % (
            self._host, self._port, API_VERSION)

        return self._do_search(url, term, page)

    def search_artist(self, term, page=None):
        """The first page is numbered 1!"""
        url = "http://%s:%s/search/%s/artist" % (
            self._host, self._port, API_VERSION)

        return self._do_search(url, term, page)

    def search_track(self, term, page=None):
        """The first page is numbered 1!"""
        url = "http://%s:%s/search/%s/track" % (
            self._host, self._port, API_VERSION)

        return self._do_search(url, term, page)

    def _do_search(self, url, term, page):
        key = "%s:%s" % (term, page)

        res, modified, expires = self._cache_get(key)
        if res and time.time() < expires:
            return res

        query = {"q": term.encode('UTF-8')}

        if page is not None:
            query["page"] = str(page)

        fp, new_modified, new_expires = self._get_url(url, query, modified)

        if fp: # We got data, sweet
            res = parse_search_doc(fp)

        self._cache_put(key, res, new_modified or modified, new_expires or expires)

        return res

    def _cache_get(self, key):
        """Get a tuple containing data, last-modified, expires.
        If entry is not in cache return None, 0, 0
        """
        entry = None
        if self.cache is not None:
            entry = self.cache.get(key)

        return entry or (None, 0, 0)

    def _cache_put(self, key, value, modified, expires):
        """Inverse of _cache_put"""
        if self.cache is not None:
            self.cache[key] = value, modified, expires

# This is an instance of the metadata module used for module level
# operations. Only suitable for simple stuff. Normally one should
# instanciate Metadata manually with appropriate options, especially
# with regards to caching
_module_meta_instance = Metadata()

lookup = _module_meta_instance.lookup
search_album = _module_meta_instance.search_album
search_artist = _module_meta_instance.search_artist
search_track = _module_meta_instance.search_track
