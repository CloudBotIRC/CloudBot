import responses
import pytest

from plugins.fishbans import fishbans, bancount

test_user = "notch"

test_api = """
{"success":true,"stats":{"username":"notch","uuid":"069a79f444e94726a5befca90e38aaf5","totalbans":11,"service":{"mcbans":0,"mcbouncer":11,"mcblockit":0,"minebans":0,"glizer":0}}}
"""
test_api_single = """
{"success":true,"stats":{"username":"notch","uuid":"069a79f444e94726a5befca90e38aaf5","totalbans":1,"service":{"mcbans":0,"mcbouncer":1,"mcblockit":0,"minebans":0,"glizer":0}}}
"""
test_api_none = """
{"success":true,"stats":{"username":"notch","uuid":"069a79f444e94726a5befca90e38aaf5","totalbans":0,"service":{"mcbans":0,"mcbouncer":0,"mcblockit":0,"minebans":0,"glizer":0}}}
"""
test_api_failed = """
{"success":false}
"""

bans_reply = "The user \x02notch\x02 has \x0211\x02 bans - http://fishbans.com/u/notch/"
count_reply = "Bans for \x02notch\x02: mcbouncer: \x0211\x02 - http://fishbans.com/u/notch/"

bans_reply_single = "The user \x02notch\x02 has \x021\x02 ban - http://fishbans.com/u/notch/"

bans_reply_none = "The user \x02notch\x02 has no bans - http://fishbans.com/u/notch/"
count_reply_none = "The user \x02notch\x02 has no bans - http://fishbans.com/u/notch/"

reply_failed = "Could not fetch ban data for notch."
reply_error = "Could not fetch ban data from the Fishbans API:"


class DummyBot:
    user_agent = "CloudBot/3.0"


class TestBans:
    @responses.activate
    def test_bans(self):
        """
        tests fishbans with a successful API response having multiple bans
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', body=test_api)

        assert fishbans(test_user, DummyBot) == bans_reply

    @responses.activate
    def test_bans_single(self):
        """
        tests fishbans with a successful API response having a single ban
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_single)

        assert fishbans(test_user, DummyBot) == bans_reply_single

    @responses.activate
    def test_bans_failed(self):
        """
        tests fishbans with a failed API response
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_failed)

        assert fishbans(test_user, DummyBot) == reply_failed

    @responses.activate
    def test_bans_none(self):
        """
        tests fishbans with a successful API response having no bans
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_none)

        assert fishbans(test_user, DummyBot) == bans_reply_none

    @responses.activate
    def test_bans_error(self):
        """
        tests fishbans with a HTTP error
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', status=404)

        assert fishbans(test_user, DummyBot).startswith(reply_error)


class TestCount:
    @responses.activate
    def test_count(self):
        """
        tests bancount with a successful API response having multiple bans
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', body=test_api)

        assert bancount(test_user, DummyBot) == count_reply

    @responses.activate
    def test_count_failed(self):
        """
        tests bancount with a failed API response
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_failed)

        assert bancount(test_user, DummyBot) == reply_failed

    @responses.activate
    def test_count_none(self):
        """
        tests bancount with a successful API response having no bans
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_none)

        assert bancount(test_user, DummyBot) == count_reply_none

    @responses.activate
    def test_count_error(self):
        """
        tests bancount with a HTTP error
        """
        responses.add(responses.GET, 'http://api.fishbans.com/stats/notch/', status=404)

        assert bancount(test_user, DummyBot).startswith(reply_error)