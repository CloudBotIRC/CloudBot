import httpretty
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
reply_error = "Could not fetch ban data from the Fishbans API: 404 Client Error: Not Found"


class DummyBot():
    user_agent = "CloudBot/3.0"


@pytest.mark.httpretty
def test_bans():
    """
    tests fishbans with a successful API response having multiple bans
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', body=test_api)

    assert fishbans(test_user, DummyBot) == bans_reply


@pytest.mark.httpretty
def test_bans_single():
    """
    tests fishbans with a successful API response having a single ban
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_single)

    assert fishbans(test_user, DummyBot) == bans_reply_single

@pytest.mark.httpretty
def test_bans_failed():
    """
    tests fishbans with a failed API response
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_failed)

    assert fishbans(test_user, DummyBot) == reply_failed


@pytest.mark.httpretty
def test_bans_none():
    """
    tests fishbans with a successful API response having no bans
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_none)

    assert fishbans(test_user, DummyBot) == bans_reply_none


@pytest.mark.httpretty
def test_bans_error():
    """
    tests fishbans with a HTTP error
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', status=404)

    assert fishbans(test_user, DummyBot) == reply_error


@pytest.mark.httpretty
def test_count():
    """
    tests bancount with a successful API response having multiple bans
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', body=test_api)

    assert bancount(test_user, DummyBot) == count_reply


@pytest.mark.httpretty
def test_count_failed():
    """
    tests bancount with a failed API response
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_failed)

    assert bancount(test_user, DummyBot) == reply_failed


@pytest.mark.httpretty
def test_count_none():
    """
    tests bancount with a successful API response having no bans
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', body=test_api_none)

    assert bancount(test_user, DummyBot) == count_reply_none


@pytest.mark.httpretty
def test_count_error():
    """
    tests bancount with a HTTP error
    """
    httpretty.register_uri(httpretty.GET, 'http://api.fishbans.com/stats/notch/', status=404)

    assert bancount(test_user, DummyBot) == reply_error