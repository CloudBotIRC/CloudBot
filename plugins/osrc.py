from bs4 import BeautifulSoup

from util import hook, http, web


user_url = "http://osrc.dfm.io/{}"


@hook.command
def osrc(inp):
    """osrc <github user> -- Gets an Open Source Report Card for <github user>"""

    user_nick = inp.strip()
    url = user_url.format(user_nick)

    try:
        soup = http.get_soup(url)
    except (http.HTTPError, http.URLError):
        return "Couldn't find any stats for this user."

    report = soup.find("div", {"id": "description"}).find("p").get_text()

    # Split and join to remove all the excess whitespace, slice the
    # string to remove the trailing full stop.
    report = " ".join(report.split())[:-1]

    short_url = web.try_isgd(url)

    return "{} - {}".format(report, short_url)
