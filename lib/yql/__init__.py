"""
Python YQL
==========

YQL client for Python

Author: Stuart Colville http://muffinresearch.co.uk/
Docs at: http://python-yql.org/

TODO: More granular error handling

"""
import json
import re
import time
import pprint
from urlparse import urlparse
from urllib import urlencode
from httplib2 import Http

from yql.utils import get_http_method, clean_url, clean_query
from yql.logger import get_logger
import oauth2 as oauth

try:
    from urlparse import parse_qs, parse_qsl
except ImportError: # pragma: no cover
    from cgi import parse_qs, parse_qsl


__author__ = 'Stuart Colville'
__version__ = '0.7.5'
__all__ = ['Public', 'TwoLegged', 'ThreeLegged']


QUERY_PLACEHOLDER = re.compile(r"[ =]@(?P<param>[a-z].*?\b)", re.IGNORECASE)


REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
ACCESS_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_token'
AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'


PUBLIC_ENDPOINT = "query.yahooapis.com/v1/public/yql"
PRIVATE_ENDPOINT = "query.yahooapis.com/v1/yql"
HTTP_SCHEME = "http:"
HTTPS_SCHEME = "https:"


yql_logger = get_logger()


class YQLObj(object):
    """A YQLObject is the object created as the result of a YQL query"""

    def __init__(self, result_dict):
        """Init query object"""
        self._raw = result_dict and result_dict.get('query') or {}

    @property
    def raw(self):
        """The raw data response"""
        return self._raw

    @property
    def uri(self):
        """The uri used to query the YQL API"""
        return self._raw.get('uri')

    @property
    def query_params(self):
        """The query parameters of the uri used to call the YQL API"""
        if self.uri:
            q_string = urlparse(self.uri)[4]
            return dict(parse_qsl(q_string))
        else:
            return {}

    @property
    def results(self):
        """The query results dict."""
        return self._raw.get('results')

    def one(self):
        """Return just one result directly."""
        rows = self.rows
        if len(rows) > 1:
            raise NotOneError, "More than one result"
        else:
            return rows[0]

    @property
    def rows(self):
        """Get a list of rows returned by the query.

        Results is a dict with one key but that key changes depending on the results
        This provides a way of getting at the rows list in an arbitrary way.

        Added in version: 0.6 fixes results with 1 item so that they are still
        returned within a list.

        """
        result = []
        if self.results:
            vals = self.results.values()
            if len(vals) == 1:
                result = self.results.values()[0]

        if self.count == 1 and result:
            result = [result]

        return result

    @property
    def query(self):
        """The YQL query"""
        return self.query_params.get('q')

    @property
    def lang(self):
        """The language"""
        return self._raw.get('lang')

    @property
    def count(self):
        """The results count"""
        count = self._raw.get('count')
        if count:
            return int(count)

    @property
    def diagnostics(self):
        """The query diagnostics"""
        return self._raw.get('diagnostics')

    def pprint_raw(self, indent=4): # pragma: no cover
        """Pretty print the raw data"""
        pprint.pprint(self._raw, indent=indent)

    def pformat_raw(self, indent=4): # pragma: no cover
        """Pretty format the raw data"""
        return pprint.pformat(self._raw, indent=indent)


class YQLError(Exception):
    """Default Error"""

    def __init__(self, resp, content, url=None, query=None):
        yql_logger.error("%s", content)
        yql_logger.error("Error Response: %s", resp)
        yql_logger.error("Error url: %s", url)
        self.response = resp
        self.content = content
        self.url = url
        self.query = query

    def __str__(self):
        """Return the error message.

        Attempt to parse the json if it fails
        simply return the content attribute instead.

        """
        try:
            content = json.loads(self.content)
        except:
            content = {}

        if content and content.get("error") and content["error"].get(
                                                        "description"):
            return content['error']['description']
        else:
            if isinstance(self.content, basestring):
                return self.content
            else:
                return repr(self.content)


class NotOneError(Exception):
    """Not One Error."""

    def  __init__(self, message):
        self.message = message

    def  __str__(self):
        """Return the error message"""
        return self.message


class Public(object):
    """Class for making public YQL queries"""

    def __init__(self, api_key=None, shared_secret=None, httplib2_inst=None):
        """Init the base class.

        Optionally you can pass in an httplib2 instance which allows you
        to set-up the instance in a different way for your own uses.

        Also it's very helpful in a testing scenario.

        """
        self.api_key = api_key
        self.secret = shared_secret
        self.http = httplib2_inst or Http()
        self.scheme = HTTPS_SCHEME
        self.__endpoint = PUBLIC_ENDPOINT
        self.uri = self.get_endpoint_uri()

    def get_endpoint_uri(self):
        """Get endpoint"""
        return "http://%s" % self.endpoint

    def get_endpoint(self):
        """Gets the endpoint for requests"""
        return self.__endpoint

    def set_endpoint(self, value):
        """Sets the endpoint and updates the uri"""
        if value in (PRIVATE_ENDPOINT, PUBLIC_ENDPOINT):
            self.__endpoint = value
            self.uri = self.get_endpoint_uri()
        else:
            raise ValueError, "Invalid endpoint: %s" % value


    def get_query_params(self, query, params, **kwargs):
        """Get the query params and validate placeholders"""
        query_params = {}
        keys_from_query = self.get_placeholder_keys(query)

        if keys_from_query and not params or (
                                     params and not hasattr(params, 'get')):

            raise ValueError, "If you are using placeholders a dictionary "\
                                                "of substitutions is required"

        elif not keys_from_query and params and hasattr(params, 'get'):
            raise ValueError, "You supplied a dictionary of substitutions "\
                                "but the query doesn't have any placeholders"

        elif keys_from_query and params:
            keys_from_params = params.keys()

            if set(keys_from_query) != set(keys_from_params):
                raise ValueError, "Parameter keys don't match the query "\
                                                                "placeholders"
            else:
                query_params.update(params)

        query_params['q'] = query
        query_params['format'] = 'json'

        env = kwargs.get('env')
        if env:
            query_params['env'] = env

        return query_params

    @staticmethod
    def get_placeholder_keys(query):
        """Gets the @var placeholders

        http://developer.yahoo.com/yql/guide/var_substitution.html

        """
        result = []
        for match in  QUERY_PLACEHOLDER.finditer(query):
            result.append(match.group('param'))

        if result:
            yql_logger.debug("placeholder_keys: %s", result)

        return result

    def get_uri(self, query, params=None, **kwargs):
        """Get the the request url"""
        params = self.get_query_params(query, params, **kwargs)
        query_string = urlencode(params)
        uri =  '%s?%s' % (self.uri, query_string)
        uri = clean_url(uri)
        return uri

    def execute(self, query, params=None, **kwargs):
        """Execute YQL query"""
        query = clean_query(query)
        url = self.get_uri(query, params, **kwargs)
        # Just in time change to https avoids
        # invalid oauth sigs
        if self.scheme == HTTPS_SCHEME:
            url = url.replace(HTTP_SCHEME, HTTPS_SCHEME)
        yql_logger.debug("executed url: %s", url)
        http_method = get_http_method(query)
        if http_method in ["DELETE", "PUT", "POST"]:
            data = {"q": query}

            # Encode as json and set Content-Type header
            # to reflect we are sending JSON
            # Fixes LP: 629064
            data = json.dumps(data)
            headers = {"Content-Type": "application/json"}
            resp, content = self.http.request(
                            url, http_method, headers=headers, body=data)
            yql_logger.debug("body: %s", data)
        else:
            resp, content = self.http.request(url, http_method)
        yql_logger.debug("http_method: %s", http_method)
        if resp.get('status') == '200':
            return YQLObj(json.loads(content))
        else:
            raise YQLError, (resp, content)

    endpoint = property(get_endpoint, set_endpoint)


class TwoLegged(Public):
    """Two legged Auth is simple request which is signed prior to sending"""

    def __init__(self, api_key, shared_secret, httplib2_inst=None):
        """Override init to ensure required args"""
        super(TwoLegged, self).__init__(api_key, shared_secret, httplib2_inst)
        self.endpoint = PRIVATE_ENDPOINT
        self.scheme = HTTPS_SCHEME
        self.hmac_sha1_signature = oauth.SignatureMethod_HMAC_SHA1()
        self.plaintext_signature = oauth.SignatureMethod_PLAINTEXT()

    @staticmethod
    def get_base_params():
        """Set-up the basic parameters needed for a request"""

        params = {}
        params['oauth_version'] = "1.0"
        params['oauth_nonce'] = oauth.generate_nonce()
        params['oauth_timestamp'] = int(time.time())
        return params


    def __two_legged_request(self, resource_url, parameters=None, method=None):
        """Sign a request for two-legged authentication"""

        params = self.get_base_params()
        if parameters:
            params.update(parameters)

        yql_logger.debug("params: %s", params)
        yql_logger.debug("resource_url: %s", resource_url)
        if not method:
            method = "GET"

        consumer = oauth.Consumer(self.api_key, self.secret)
        request = oauth.Request(method=method, url=resource_url,
                                                        parameters=params)
        request.sign_request(self.hmac_sha1_signature, consumer, None)
        return request


    def get_uri(self, query, params=None, **kwargs):
        """Get the the request url"""
        query_params = self.get_query_params(query, params, **kwargs)

        http_method = get_http_method(query)
        request = self.__two_legged_request(self.uri,
                       parameters=query_params, method=http_method)
        uri = "%s?%s" % (self.uri, request.to_postdata())
        uri = clean_url(uri)
        return uri


class ThreeLegged(TwoLegged):

    """
    Three-legged Auth is used when it involves private data such as a
    user's contacts.

    Three-legged auth is most likely to be used in a web-site or
    web-accessible application. Three-legged auth requires the user
    to authenticate the request through the Yahoo login.

    Three-legged auth requires the implementation to:

    * Request a token
    * Get a authentication url
    * User uses the auth url to login which will redirect to a callback
      or shows a verfier string on screen
    * Verifier is read at the callback url or manually provided to get
      the access token
    * resources is access

    For an implementation this will require calling the following methods
    in order the first time the user needs to authenticate

    * :meth:`get_token_and_auth_url` (returns a token and the auth url)
    * get verifier through callback or from screen
    * :meth:`get_access_token`  (returns the access token)
    * :meth:`execute` - makes the request to the protected resource.

    Once the access token has been provided subsequent requests can re-use it.

    Access tokens expire after 1 hour, however they can be refreshed with
    the :meth:`refresh_token` method


    """

    def __init__(self, api_key, shared_secret, httplib2_inst=None):
        """Override init to add consumer"""
        super(ThreeLegged, self).__init__(
                                    api_key, shared_secret, httplib2_inst)

        self.scheme = HTTP_SCHEME
        self.endpoint = PRIVATE_ENDPOINT
        self.consumer = oauth.Consumer(self.api_key, self.secret)

    def get_token_and_auth_url(self, callback_url=None):
        """First step is to get the token and then send the request that
        provides the auth URL

        Returns a tuple of token and the authorisation URL.

        """

        client = oauth.Client(self.consumer)

        params = {}
        params['oauth_callback'] = callback_url or 'oob'

        request = oauth.Request(parameters=params)
        url = REQUEST_TOKEN_URL
        resp, content = client.request(url, "POST", request.to_postdata())

        if resp.get('status') == '200':
            token = oauth.Token.from_string(content)
            yql_logger.debug("token: %s", token)
            data = dict(parse_qsl(content))
            yql_logger.debug("data: %s", data)
            return token, data['xoauth_request_auth_url']
        else:
            raise YQLError, (resp, content, url)


    def get_access_token(self, token, verifier):

        """Get the access token

        The verifier (required) should have been provided to the
        user following login to at the url returned
        by the :meth:`get_token_and_auth_url` method.

        If not you will need need to extract the auth_verifier
        parameter from your callback url on the site where you
        are implementing 3-legged auth in order to pass it to this
        function.

        The access token can be stored and re-used for subsequent
        calls.

        The stored token will also need to be refreshed periodically
        with :meth:`refresh_token`

        """

        params = {}
        params['oauth_verifier'] = verifier

        oauth_request = oauth.Request.from_consumer_and_token(
                               self.consumer, token=token,
                               http_url=ACCESS_TOKEN_URL,
                               http_method="POST",
                               parameters=params)

        yql_logger.debug("oauth_request: %s", oauth_request)
        oauth_request.sign_request(
                self.hmac_sha1_signature, self.consumer, token)

        url = oauth_request.to_url()

        yql_logger.debug("oauth_url: %s", url)
        postdata = oauth_request.to_postdata()
        yql_logger.debug("oauth_postdata: %s", postdata)
        resp, content = self.http.request(url, "POST", postdata)

        if resp.get('status') == '200':
            access_token = YahooToken.from_string(content)
            access_token.timestamp = oauth_request['oauth_timestamp']
            return access_token
        else:
            raise YQLError, (resp, content, url)


    def check_token(self, token):
        """Check to see if a token has expired"""

        if not hasattr(token, 'timestamp'):
            raise AttributeError, 'token doesn\'t have a timestamp attrbute'

        if (int(token.timestamp) + 3600) < time.time():
            token = self.refresh_token(token)

        return token


    def refresh_token(self, token):
        """Access Tokens only last for one hour from the point of being issued.

        When a token has expired it needs to be refreshed this method takes an
        expired token and refreshes it.

        token parameter can be either a token object or a token string.

        """
        if not hasattr(token, "key"):
            token = YahooToken.from_string(token)

        params = self.get_base_params()
        params['oauth_token'] = token.key
        params['oauth_token_secret'] = token.secret
        params['oauth_session_handle'] = token.session_handle

        oauth_request = oauth.Request.from_consumer_and_token(
                               self.consumer, token=token,
                               http_url=ACCESS_TOKEN_URL,
                               http_method="POST",
                               parameters=params)

        yql_logger.debug("oauth_request: %s", oauth_request)
        oauth_request.sign_request(
                self.hmac_sha1_signature, self.consumer, token)

        url = oauth_request.to_url()
        yql_logger.debug("oauth_url: %s", url)
        postdata = oauth_request.to_postdata()
        yql_logger.debug("oauth_postdata: %s", postdata)
        resp, content = self.http.request(url, "POST", postdata)

        if resp.get('status') == '200':
            access_token = YahooToken.from_string(content)
            yql_logger.debug("oauth_access_token: %s", access_token)
            access_token.timestamp = oauth_request['oauth_timestamp']
            return access_token
        else:
            raise YQLError, (resp, content, url)

    def get_uri(self, query, params=None, **kwargs):
        """Get the the request url"""
        query_params = self.get_query_params(query, params, **kwargs)

        token = kwargs.get("token")

        if hasattr(token, "yahoo_guid"):
            query_params["oauth_yahoo_guid"] = getattr(token, "yahoo_guid")

        if not token:
            raise ValueError, "Without a token three-legged-auth cannot be"\
                                                              " carried out"

        yql_logger.debug("query_params: %s", query_params)
        http_method = get_http_method(query)
        oauth_request = oauth.Request.from_consumer_and_token(
                                        self.consumer, http_url=self.uri,
                                        token=token, parameters=query_params,
                                        http_method=http_method)
        yql_logger.debug("oauth_request: %s", oauth_request)
        # Sign request
        oauth_request.sign_request(
                            self.hmac_sha1_signature, self.consumer, token)

        yql_logger.debug("oauth_signed_request: %s", oauth_request)
        uri = "%s?%s" % (self.uri,  oauth_request.to_postdata())
        return uri.replace('+', '%20').replace('%7E', '~')


class YahooToken(oauth.Token):
    """A subclass of oauth.Token with the addition of a place to
    stash the session_handler which is required for token refreshing

    """

    @staticmethod
    def from_string(data_string):
        """Deserializes a token from a string like one returned by

        `to_string()`."""

        if not len(data_string):
            raise ValueError("Invalid parameter string.")

        params = parse_qs(data_string, keep_blank_values=False)
        if not len(params):
            raise ValueError("Invalid parameter string.")

        try:
            key = params['oauth_token'][0]
        except Exception:
            raise ValueError("'oauth_token' not found in OAuth request.")

        try:
            secret = params['oauth_token_secret'][0]
        except Exception:
            raise ValueError("'oauth_token_secret' not found in "
                "OAuth request.")

        token = YahooToken(key, secret)

        session_handle = params.get('oauth_session_handle')
        if session_handle:
            setattr(token, 'session_handle', session_handle[0])

        timestamp = params.get('token_creation_timestamp')
        if timestamp:
            setattr(token, 'timestamp', timestamp[0])

        try:
            token.callback_confirmed = params['oauth_callback_confirmed'][0]
        except KeyError:
            pass # 1.0, no callback confirmed.

        return token


    def to_string(self):
        """Returns this token as a plain string, suitable for storage.
        The resulting string includes the token's secret, so you should never
        send or store this string where a third party can read it.

        """

        data = {
            'oauth_token': self.key,
            'oauth_token_secret': self.secret,
        }

        if hasattr(self, 'session_handle'):
            data['oauth_session_handle'] = self.session_handle

        if hasattr(self, 'timestamp'):
            data['token_creation_timestamp'] = self.timestamp

        if self.callback_confirmed is not None:
            data['oauth_callback_confirmed'] = self.callback_confirmed

        return urlencode(data)
