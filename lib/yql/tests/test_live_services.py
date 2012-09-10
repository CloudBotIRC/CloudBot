"""Tests against live services.

*** SKIPPED BY DEFAULT ***

These tests won't normally be run, as part of the main test suite but are run by
our hudson instance to tell us should Yahoo's API change in some way that will
break python-yql.

Note to end-users: These tests are dependent on defining a secrets file with API
keys and other secrets which are required to carry out these tests.

If the secrets file isn't present the tests are skipped

"""
import os
import sys
from time import time
from unittest import TestCase

from nose.plugins.skip import SkipTest

import yql
from yql.storage import FileTokenStore


SECRETS_DIR = os.path.join(os.path.dirname(__file__), "../../../secrets")
CACHE_DIR = os.path.abspath(os.path.join(SECRETS_DIR, "cache"))

try:
    if SECRETS_DIR not in sys.path:
        sys.path.append(SECRETS_DIR)

    from secrets import *
except ImportError:
    raise SkipTest("Unable to find secrets directory")


class LiveTestCase(TestCase):
    """A test case containing live tests"""

    def test_write_bitly_url(self):
        """Test writing bit.ly url"""

        query = """USE 'http://www.datatables.org/bitly/bit.ly.shorten.xml';
           SELECT * from bit.ly.shorten where login='%s' and apiKey='%s' and
           longUrl='http://yahoo.com'""" % (BITLY_USER, BITLY_API_KEY)

        y = yql.TwoLegged(YQL_API_KEY, YQL_SHARED_SECRET)
        res = y.execute(query)
        assert res.one()["data"]["url"] == "http://yhoo.it/9PPTOr"

    def test_public_request(self):
        """Test public two-legged request to flickr"""
        query = """select * from flickr.photos.search where
                   text="panda" and api_key='%s' LIMIT 3""" % FLICKR_API_KEY
        y = yql.TwoLegged(YQL_API_KEY, YQL_SHARED_SECRET)
        res = y.execute(query)
        assert len(res.rows) == 3

    def test_two_legged_weather_select(self):
        """Tests the weather tables using two-legged"""
        query = """select * from weather.forecast where location in
                (select id from xml where
                url='http://xoap.weather.com/search/search?where=london'
                and itemPath='search.loc')"""
        y = yql.TwoLegged(YQL_API_KEY, YQL_SHARED_SECRET)
        res = y.execute(query)
        assert len(res.rows) > 1

    def test_update_social_status(self):
        """Updates status"""
        y = yql.ThreeLegged(YQL_API_KEY, YQL_SHARED_SECRET)

        timestamp = time()
        query = """UPDATE social.profile.status
                   SET status='Using YQL. %s Update'
                   WHERE guid=me"""  % timestamp

        token_store = FileTokenStore(CACHE_DIR, secret='gsfdsfdsfdsfs')
        stored_token = token_store.get('foo')

        if not stored_token:
            # Do the dance
            request_token, auth_url = y.get_token_and_auth_url()
            print "Visit url %s and get a verifier string" % auth_url
            verifier = raw_input("Enter the code: ")
            token = y.get_access_token(request_token, verifier)
            token_store.set('foo', token)
        else:
            # Check access_token is within 1hour-old and if not refresh it
            # and stash it
            token = y.check_token(stored_token)
            if token != stored_token:
                token_store.set('foo', token)

        res = y.execute(query, token=token)
        assert res.rows[0] == "ok"
        new_query = """select message from social.profile.status where guid=me"""
        res = y.execute(new_query, token=token)
        assert res.rows[0].get("message") == "Using YQL. %s Update" % timestamp

    def test_update_meme_status(self):
        """Updates status"""
        y = yql.ThreeLegged(YQL_API_KEY, YQL_SHARED_SECRET)
        query = 'INSERT INTO meme.user.posts (type, content) VALUES("text", "test with pythonyql")'
        token_store = FileTokenStore(CACHE_DIR, secret='fjdsfjllds')

        store_name = "meme"
        stored_token = token_store.get(store_name)
        if not stored_token:
            # Do the dance
            request_token, auth_url = y.get_token_and_auth_url()
            print "Visit url %s and get a verifier string" % auth_url
            verifier = raw_input("Enter the code: ")
            token = y.get_access_token(request_token, verifier)
            token_store.set(store_name, token)
        else:
            # Check access_token is within 1hour-old and if not refresh it
            # and stash it
            token = y.check_token(stored_token)
            if token != stored_token:
                token_store.set(store_name, token)

        # post a meme
        res = y.execute(query, token=token)
        assert y.uri == "http://query.yahooapis.com/v1/yql"
        assert res.rows[0].get("message") == "ok"

        pubid = None
        if res.rows[0].get("post") and res.rows[0]["post"].get("pubid"):
            pubid = res.rows[0]["post"]["pubid"]

        # Delete the post we've just created
        query = 'DELETE FROM meme.user.posts WHERE pubid=@pubid'
        res2 = y.execute(query, token=token, params={"pubid": pubid})
        assert res2.rows[0].get("message") == "ok"

    def test_check_env_var(self):
        """Testing env variable"""
        y = yql.Public()
        env = "http://datatables.org/alltables.env"
        query = "SHOW tables;"
        res = y.execute(query, env=env)
        assert res.count >= 800

    def test_xpath_works(self):
        y = yql.Public()
        query = """SELECT * FROM html
                   WHERE url='http://google.co.uk'
                   AND xpath="//input[contains(@name, 'q')]"
                   LIMIT 10"""
        res = y.execute(query)
        assert res.rows[0].get("title") == "Search"


