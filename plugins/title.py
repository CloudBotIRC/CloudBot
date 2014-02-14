from bs4 import BeautifulSoup

from util import hook, http, urlnorm


@hook.command
def title(inp):
    """title <url> -- gets the title of a web page"""
    url = urlnorm.normalize(inp.encode('utf-8'), assume_scheme="http")

    try:
        page = http.open(url)
        real_url = page.geturl()
        soup = BeautifulSoup(page.read())
    except (http.HTTPError, http.URLError):
        return "Could not fetch page."

    page_title = soup.find('title').contents[0]

    if not page_title:
        return "Could not find title."

    return u"{} [{}]".format(page_title, real_url)
