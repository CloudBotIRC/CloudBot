import requests
from bs4 import BeautifulSoup

from cloudbot import hook


@hook.command("wordoftheday", "word", autohelp=False)
def wordoftheday():
    """- Gets the word of the day from http://www.merriam-webster.com/word-of-theday"""
    page = requests.get('http://merriam-webster.com/word-of-the-day')

    soup = BeautifulSoup(page.text)

    word = soup.find('strong', {'class': 'main_entry_word'}).text
    function = soup.find('p', {'class': 'word_function'}).text
    definition = soup.find('div', {'class': 'scnt'}).find('span', {'class': 'ssens'}).text

    return "The word of the day is: \x02{}\x02 ({}){}".format(word, function, definition)
