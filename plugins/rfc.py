from cloudbot import hook
from cloudbot.util import database, colors, web
from urllib.request import urlopen
from bs4 import BeautifulSoup

@hook.command()
def rfc(text, notice):
    """<rfc> <number> - Gets the title and a link to an RFC"""
    text = text.strip().lower()
    url = "http://tools.ietf.org/html/rfc{}".format(text)
    data = str(urlopen(url).read())
    soup = BeautifulSoup(data)
    title = soup.title.string
    return "{} - {}".format(title, url)

