from util import hook, http, urlnorm
from bs4 import BeautifulSoup


@hook.command
def title(inp):
    "title <url> -- gets the title of a web page"
    url = urlnorm.normalize(inp.encode('utf-8'), assume_scheme="http")

    try:
        page = http.open(url)
        real_url = page.geturl()
        soup = BeautifulSoup(page.read())
    except (http.HTTPError, http.URLError):
        return "Could not fetch page."

    title = soup.find('title').contents[0]

    if not title:
        return "Could not find title."

    return u"{} [{}]".format(title, real_url)
