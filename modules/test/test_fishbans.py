import json
import pytest

from modules.fishbans import fishbans, bancount
from util import http

test_user = "notch"

test_api = """
{"success":true,"stats":{"username":"notch","uuid":"069a79f444e94726a5befca90e38aaf5","totalbans":11,"service":{"mcbans":0,"mcbouncer":11,"mcblockit":0,"minebans":0,"glizer":0}}}
"""
test_api_no_bans = """
{"success":true,"stats":{"username":"notch","uuid":"069a79f444e94726a5befca90e38aaf5","totalbans":0,"service":{"mcbans":0,"mcbouncer":0,"mcblockit":0,"minebans":0,"glizer":0}}}
"""
test_api_failed = """
{"success":false}
"""

bans_reply = "The user \x02notch\x02 has \x0211\x02 ban(s) - http://fishbans.com/u/notch/"
count_reply = "Bans for \x02notch\x02: mcbouncer: \x0211\x02 - http://fishbans.com/u/notch/"

failed_bans_reply = "Could not fetch ban data for notch."
failed_count_reply = "Could not fetch ban data for notch."

no_bans_reply = "The user \x02notch\x02 has no bans - http://fishbans.com/u/notch/"
no_count_reply = "The user \x02notch\x02 has no bans - http://fishbans.com/u/notch/"


def test_bans(monkeypatch):
    """ tests fishbans with a successful API response having a number of bans
    """

    def fake_http(url):
        assert url == "http://api.fishbans.com/stats/notch/"
        return json.loads(test_api)

    monkeypatch.setattr(http, "get_json", fake_http)

    assert fishbans(test_user) == bans_reply


def test_bans_failed(monkeypatch):
    """ tests fishbans with a failed API response
    """

    def fake_http(url):
        assert url == "http://api.fishbans.com/stats/notch/"
        return json.loads(test_api_failed)

    monkeypatch.setattr(http, "get_json", fake_http)

    assert fishbans(test_user) == failed_bans_reply


def test_bans_no_bans(monkeypatch):
    """ tests fishbans with a successful API response having no bans
    """

    def fake_http(url):
        assert url == "http://api.fishbans.com/stats/notch/"
        return json.loads(test_api_no_bans)

    monkeypatch.setattr(http, "get_json", fake_http)

    assert fishbans(test_user) == no_bans_reply


def test_count(monkeypatch):
    def fake_http(url):
        assert url == "http://api.fishbans.com/stats/notch/"
        return json.loads(test_api)

    monkeypatch.setattr(http, "get_json", fake_http)

    assert bancount(test_user) == count_reply


def test_count_failed(monkeypatch):
    def fake_http(url):
        assert url == "http://api.fishbans.com/stats/notch/"
        return json.loads(test_api_failed)

    monkeypatch.setattr(http, "get_json", fake_http)

    assert bancount(test_user) == failed_count_reply


def test_count_no_bans(monkeypatch):
    def fake_http(url):
        assert url == "http://api.fishbans.com/stats/notch/"
        return json.loads(test_api_no_bans)

    monkeypatch.setattr(http, "get_json", fake_http)

    assert bancount(test_user) == no_count_reply
