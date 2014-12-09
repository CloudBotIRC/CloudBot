import requests
import bs4

from cloudbot import hook
from cloudbot.util import web


class SteamError(Exception):
    pass


CALC_URL = "https://steamdb.info/calculator/"


def get_data(user, currency="us"):
    """
    takes a steam user ID and returns a dict containing info about the games the user owns
    :type user: str
    :type currency: str
    :return: dict
    """
    data = {}

    # form the request
    params = {'player': user, 'currency': currency}

    # get the page
    try:
        request = requests.get(CALC_URL, params=params)
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise SteamError("Could not get user info: {}".format(e))

    # parse that page!
    soup = bs4.BeautifulSoup(request.text)

    # get all the data we need
    try:
        data["name"] = soup.find("h1", {"class": "header-title"}).find("a").text
        data["url"] = request.url

        data["value"] = soup.find("h1", {"class": "calculator-price"}).text
        data["value_sales"] = soup.find("h1", {"class": "calculator-price-lowest"}).text

        data["count"] = soup.find("div",
                                  {"class": "pull-right price-container"}).find("p").find("span", {"class":
                                                                                                       "number"}).text
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

    return "\x02{name}\x02 has \x02{count}\x02 games with a total value of \x02{value}\x02!" \
           " (\x02{value_sales}\x02 during sales) - {short_url}".format(**data)