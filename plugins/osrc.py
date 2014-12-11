import requests
from bs4 import BeautifulSoup

from cloudbot import hook
from cloudbot.util import web

user_url = "http://osrc.dfm.io/{}"


@hook.command()
def osrc(text):
    """<github user> - gets an Open Source Report Card for <github user> from osrc.dfm.io"""

    user_nick = text.strip()
    url = user_url.format(user_nick)

    try:
        request = requests.get(url)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        return "Couldn't find any stats for this user."

    soup = BeautifulSoup(request.text)

    report = soup.find("div", {"id": "description"}).find("p").get_text()

    # Split and join to remove all the excess whitespace, slice the
    # string to remove the trailing full stop.
    report = " ".join(report.split())[:-1]

    short_url = web.try_shorten(url)

    return "{} - {}".format(report, short_url)
