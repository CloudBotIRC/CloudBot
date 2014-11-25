import requests
from bs4 import BeautifulSoup

from cloudbot import hook


@hook.command("wordoftheday", "word", autohelp=False)
def wordoftheday():
    """- Gets the word of the day from http://www.merriam-webster.com/word-of-the-day"""
    try:
        request = requests.get('http://merriam-webster.com/word-of-the-day')
        request.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return "Could not get word of the day: {}".format(e)

    soup = BeautifulSoup(request.text)

    word = soup.find('strong', {'class': 'main_entry_word'}).text
    function = soup.find('p', {'class': 'word_function'}).text

    # here be demons
    try:
        definition = soup.find('div', {'class': 'scnt'}).find('span', {'class': 'ssens'}).text
    except AttributeError:
        definition = ""

    return "The word of the day is: \x02{}\x02 ({}){}".format(word, function, definition)
