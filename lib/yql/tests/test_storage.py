import os
import tempfile
from unittest import TestCase

from nose.tools import raises

from yql import YahooToken
from yql.storage import BaseTokenStore, FileTokenStore, TokenStoreError


class BaseTokenStoreTest(TestCase):
    @raises(NotImplementedError)
    def test_must_implement_set(self):
        class FooStore(BaseTokenStore):
            pass
        store = FooStore()
        store.set('some name', 'some token')

    @raises(NotImplementedError)
    def test_must_implement_get(self):
        class FooStore(BaseTokenStore):
            pass
        store = FooStore()
        store.get('some name')


class FileTokenStoreTest(TestCase):
    @raises(TokenStoreError)
    def test_must_be_instanced_with_an_existant_path(self):
        FileTokenStore('/some/inexistant/path')

    def test_saves_token_string_to_filesystem(self):
        directory = tempfile.mkdtemp()
        store = FileTokenStore(directory)
        store.set('foo', '?key=some-token')
        with open(store.get_filepath('foo')) as stored_file:
            self.assertTrue('some-token' in stored_file.read())

    def test_retrieves_token_from_filesystem(self):
        directory = tempfile.mkdtemp()
        store = FileTokenStore(directory)
        store.set('foo', '?key=%s&oauth_token=some-oauth-token&'\
                  'oauth_token_secret=some-token-secret' % 'some-token')
        token = store.get('foo')
        self.assertTrue('some-token' in token.to_string())

    def test_cannot_retrieve_token_if_path_doesnt_exist(self):
        directory = tempfile.mkdtemp()
        store = FileTokenStore(directory)
        store.set('foo', '?key=%s&oauth_token=some-oauth-token&'\
                  'oauth_token_secret=some-token-secret' % 'some-token')
        os.remove(store.get_filepath('foo'))
        self.assertTrue(store.get('foo') is None)

    def test_saves_token_to_filesystem(self):
        directory = tempfile.mkdtemp()
        store = FileTokenStore(directory)
        token = YahooToken('some-token', 'some-secret')
        store.set('foo', token)
        with open(store.get_filepath('foo')) as stored_file:
            self.assertTrue('some-token' in stored_file.read())
