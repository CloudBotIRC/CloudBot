import requests
from bs4 import BeautifulSoup

from cloudbot import hook


@hook.command("wordoftheday", "word", autohelp=False)
def wordoftheday():
    """-- Gets the word of the day from http://www.merriam-webster.com/word-of-the-day"""
    try:
        request = requests.get('http://merriam-webster.com/word-of-the-day')
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get word of the day: {}".format(e)

    soup = BeautifulSoup(request.text)

    try:
        word = soup.find('div', {'class': 'wod_headword'}).text
        function = soup.find('div', {'class': 'wod_pos'}).text
    except AttributeError:
        return "Could not parse word of the day."

    # sometimes this wont work, so we do it separately
    try:
        definition = soup.find('div', {'class': 'scnt'}).find('span', {'class': 'ssens'}).text
    except AttributeError:
        definition = ""

    return "The word of the day is: \x02{}\x02 ({}){}".format(word, function, definition)
