from unittest import TestCase

from nose.tools import raises
try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl

import yql


class YahooTokenTest(TestCase):
    def test_create_yahoo_token(self):
        token = yql.YahooToken('test-key', 'test-secret')
        self.assertEqual(token.key, 'test-key')
        self.assertEqual(token.secret, 'test-secret')

    def test_y_token_to_string(self):
        token = yql.YahooToken('test-key', 'test-secret')
        token_to_string = token.to_string()
        string_data = dict(parse_qsl(token_to_string))
        self.assertEqual(string_data.get('oauth_token'), 'test-key')
        self.assertEqual(string_data.get('oauth_token_secret'), 'test-secret')

    def test_y_token_to_string2(self):
        token = yql.YahooToken('test-key', 'test-secret')

        token.timestamp = '1111'
        token.session_handle = 'poop'
        token.callback_confirmed = 'basilfawlty'

        token_to_string = token.to_string()
        string_data = dict(parse_qsl(token_to_string))
        self.assertEqual(string_data.get('oauth_token'), 'test-key')
        self.assertEqual(string_data.get('oauth_token_secret'), 'test-secret')
        self.assertEqual(string_data.get('token_creation_timestamp'), '1111')
        self.assertEqual(string_data.get('oauth_callback_confirmed'), 'basilfawlty')
        self.assertEqual(string_data.get('oauth_session_handle'), 'poop')

    def test_y_token_from_string(self):
        token_string = "oauth_token=foo&oauth_token_secret=bar&"\
                       "oauth_session_handle=baz&token_creation_timestamp=1111"
        token_from_string = yql.YahooToken.from_string(token_string)
        self.assertEqual(token_from_string.key, 'foo')
        self.assertEqual(token_from_string.secret, 'bar')
        self.assertEqual(token_from_string.session_handle, 'baz')
        self.assertEqual(token_from_string.timestamp, '1111')

    @raises(ValueError)
    def test_y_token_raises_value_error(self):
        yql.YahooToken.from_string('')

    @raises(ValueError)
    def test_y_token_raises_value_error2(self):
        yql.YahooToken.from_string('foo')

    @raises(ValueError)
    def test_y_token_raises_value_error3(self):
        yql.YahooToken.from_string('oauth_token=bar')

    @raises(ValueError)
    def test_y_token_raises_value_error4(self):
        yql.YahooToken.from_string('oauth_token_secret=bar')

    @raises(AttributeError)
    def test_y_token_without_timestamp_raises(self):
        token = yql.YahooToken('test', 'test2')
        y = yql.ThreeLegged('test', 'test2')
        y.check_token(token)

    def test_y_token_without_timestamp_raises2(self):

        def refresh_token_replacement(token):
            return 'replaced'

        y = yql.ThreeLegged('test', 'test2')
        y.refresh_token = refresh_token_replacement

        token = yql.YahooToken('test', 'test2')
        token.timestamp = 11111
        self.assertEqual(y.check_token(token), 'replaced')
