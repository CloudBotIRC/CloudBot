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

bans_reply = "The user \x02notch\x02 has \x0211\x02 ban(s) - http://fishbans.com/u/notch/"
count_reply = "Bans for \x02notch\x02: mcbouncer: \x0211\x02 - http://fishbans.com/u/notch/"

no_bans_reply = "The user \x02notch\x02 has no bans - http://fishbans.com/u/notch/"
no_count_reply = "The user \x02notch\x02 has no bans - http://fishbans.com/u/notch/"


def test_bans(monkeypatch):
    def fake_http(url):
        assert url == "http://api.fishbans.com/stats/notch/"
        return json.loads(test_api)

    monkeypatch.setattr(http, "get_json", fake_http)

    assert fishbans(test_user) == bans_reply


def test_bans_no_bans(monkeypatch):
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


def test_count_no_bans(monkeypatch):
    def fake_http(url):
        assert url == "http://api.fishbans.com/stats/notch/"
        return json.loads(test_api_no_bans)

    monkeypatch.setattr(http, "get_json", fake_http)

    assert fishbans(test_user) == no_count_reply
