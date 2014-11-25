from cloudbot import hook
from cloudbot.util import http
from bs4 import BeautifulSoup


@hook.command(autohelp=False)
def word():
    """<word> - Gets the word of the day from http://www.merriam-webster.com/word-of-theday"""
    page = http.get('http://merriam-webster.com/word-of-the-day')

    soup = BeautifulSoup(page)

    word = soup.find('strong', {'class': 'main_entry_word'}).string
    function = soup.find('p', {'class': 'word_function'}).string

    return "The word of the day is: \x02{}\x02 ({})".format(word, function)
