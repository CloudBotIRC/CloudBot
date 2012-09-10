from unittest import TestCase

from nose.tools import raises

import yql


class PublicTest(TestCase):
    @raises(ValueError)
    def test_cannot_use_unrecognizable_endpoint(self):
        y = yql.Public()
        y.endpoint = 'some-strange-endpoint'
