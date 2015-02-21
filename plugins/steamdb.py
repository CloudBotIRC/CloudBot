import re

import requests
import bs4
from cfscrape import cfscrape

from cloudbot import hook
from cloudbot.util import web


class SteamError(Exception):
    pass


def percentage(part, whole):
    return 100 * float(part) / float(whole)


CALC_URL = "https://steamdb.info/calculator/"
PLAYED_RE = re.compile(r"(.*)\((.*)%\)")


def get_data(user, currency="us"):
    """
    Takes a steam user ID and returns a dict containing info about the games the user owns
    :type user: str
    :type currency: str
    :return: dict
    """
    data = {}

    # form the request
    params = {'player': user, 'currency': currency}

    # get the page
    try:
        scraper = cfscrape.create_scraper()
        request = scraper.get(CALC_URL, params=params)

        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise SteamError("Could not get user info: {}".format(e))

    # parse that page!
    soup = bs4.BeautifulSoup(request.content)

    # get all the data we need
    try:
        data["name"] = soup.find("h1", {"class": "header-title"}).find("a").text
        data["url"] = request.url

        data["status"] = soup.find('td', text='Status').find_next('td').text

        data["value"] = soup.find("h1", {"class": "calculator-price"}).text
        data["value_sales"] = soup.find("h1", {"class": "calculator-price-lowest"}).text

        data["count"] = int(soup.find("div",
                                      {"class": "pull-right price-container"}).find("p").find("span", {"class":
                                                                                                       "number"}).text)
        played = soup.find('td', text='Games not played').find_next('td').text
        played = PLAYED_RE.search(played).groups()

        data["count_unplayed"] = int(played[0])
        data["count_played"] = data["count"] - data["count_unplayed"]

        data["percent_unplayed"] = round(percentage(data["count_unplayed"], data["count"]), 1)
        data["percent_played"] = round(percentage(data["count_played"], data["count"]), 1)

    except AttributeError:
        raise SteamError("Could not read info, does this user exist?")

    return data


@hook.command
def steamcalc(text):
    """steamcalc <username> - Gets value of steam account. Uses steamcommunity.com/id/<nickname>."""
    user = text.strip().lower()

    try:
        data = get_data(user)
    except SteamError as e:
        return "{}".format(e)

    data["short_url"] = web.try_shorten(data["url"])

    return "\x02{name}\x02 has \x02{count}\x02 games with a total value of \x02{value}\x02" \
           " (\x02{value_sales}\x02 during sales). \x02{count_unplayed}\x02" \
           " (\x02{percent_unplayed}%\x02) have never been played - {short_url}".format(**data)
