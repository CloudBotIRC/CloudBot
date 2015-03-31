from bs4 import BeautifulSoup
import requests

from cloudbot import hook


# Define some constants
tfw_api = "http://thefuckingweather.com?where={}&unit={}"


@hook.command("tfw")
def tfw(text, reply):
    """tfw <location> -- Gets the f**king weather data for <location>."""
    unit = "c"
    url = tfw_api.format(text, unit)

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text)
    except:
        return "THE FUCKING WEBSITE WON'T RESPOND"

    try:
        where = soup.find('span', {'id': 'locationDisplaySpan'}).text
        temp = soup.find('span', {'class': 'temperature'}).text
        remark = soup.find('p', {'class': 'remark'}).text
        flavor = soup.find('p', {'class': 'flavor'}).text
    except:
        return "I CAN'T FIND THAT SHIT"

    reply("{}: {}!? {} ({})".format(where, temp, remark, flavor))
