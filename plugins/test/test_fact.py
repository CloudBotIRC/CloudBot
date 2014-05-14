import urllib.error  # to allow raising urllib.U

from bs4 import BeautifulSoup
import pytest

from plugins.fact import fact
from cloudbot import http, web

testpage = """
<html>
<body>
<h1><a href="http://www.omgfacts.com/Animals/A-rhinoceros-horn-is-made-out-of-the-sam/15458" class="surprise">A rhinoceros horn is made out of the same material as human hair!</a></h1>
</body>
</html>
"""
testurl = "http://www.omgfacts.com/Animals/A-rhinoceros-horn-is-made-out-of-the-sam/15458"
testfact = "A rhinoceros horn is made out of the same material as human hair!"


def test_fact(monkeypatch):
    def fake_http(url):
        assert url == "http://www.omg-facts.com/random"
        return BeautifulSoup(testpage, 'lxml')

    def fake_isgd(url):
        assert url == testurl
        return "isgd link"

    monkeypatch.setattr(http, "get_soup", fake_http)
    monkeypatch.setattr(web, "try_isgd", fake_isgd)

    assert fact() == testfact + " - isgd link"


def test_except(monkeypatch):
    class TestException(Exception):
        # exception that shouldn't be caught
        pass

    def fake_http(url):
        assert url == "http://www.omg-facts.com/random"
        raise TestException

    def fake_isgd(url):
        assert url == testurl
        return "isgd link"

    monkeypatch.setattr(http, "get_soup", fake_http)
    monkeypatch.setattr(web, "try_isgd", fake_isgd)

    with pytest.raises(TestException):
        fact()


def test_timeout(monkeypatch):
    excepted = False

    def fake_http(url):
        nonlocal excepted  # nonlocal is a py3 thing, yay you, eh?
        assert url == "http://www.omg-facts.com/random"
        if excepted:
            return BeautifulSoup(testpage, "lxml")
        else:
            excepted = True
            raise urllib.error.URLError(1)

    def fake_isgd(url):
        assert url == testurl
        return "isgd link"

    monkeypatch.setattr(http, "get_soup", fake_http)
    monkeypatch.setattr(web, "try_isgd", fake_isgd)

    assert fact() == testfact + " - isgd link"


def test_multi_timeout(monkeypatch):
    excepted = 0

    def fake_http(url):
        nonlocal excepted  # nonlocal is a py3 thing, yay you, eh?
        assert url == "http://www.omg-facts.com/random"
        if excepted == 5:
            return BeautifulSoup(testpage, "lxml")
        else:
            excepted += 1
            raise urllib.error.URLError(1)

    def fake_isgd(url):
        assert url == testurl
        return "isgd link"

    monkeypatch.setattr(http, "get_soup", fake_http)
    monkeypatch.setattr(web, "try_isgd", fake_isgd)

    assert fact() == "Could not find a fact!"