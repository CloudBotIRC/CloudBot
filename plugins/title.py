from bs4 import BeautifulSoup

from cloudbot import hook
from cloudbot.util import http, urlnorm


@hook.command()
def title(text):
    """title <url> -- gets the title of a web page"""
    url = urlnorm.normalize(text, assume_scheme="http")

    try:
        page = http.open(url)
        real_url = page.geturl()
        soup = BeautifulSoup(page.read())
    except (http.HTTPError, http.URLError):
        return "Could not fetch page."

    page_title = soup.find('title').contents[0]

    if not page_title:
        return "Could not find title."

    return "{} [{}]".format(page_title, real_url)
