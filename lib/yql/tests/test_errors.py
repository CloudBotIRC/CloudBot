import json
from unittest import TestCase

from yql import NotOneError, YQLError


class YQLErrorTest(TestCase):
    def test_error_passed_error_string(self):
        error = YQLError(resp='some response', content='some content')
        self.assertEqual("some content", str(error))

    def test_error_passed_object(self):
        error = YQLError(resp='some response', content={"foo": 1})
        self.assertEqual(repr({"foo": 1}), str(error))

    def test_error_passed_json(self):
        content = {
            'error': {
                'description': 'some description',
            }
        }
        error = YQLError(resp='some response', content=json.dumps(content))
        self.assertEqual("some description", str(error))


class NotOneErrorTest(TestCase):
    def test_is_represented_by_message_as_json(self):
        error = NotOneError('some message')
        self.assertEqual("some message", str(error))
