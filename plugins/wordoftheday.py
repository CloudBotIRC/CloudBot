from cloudbot import hook
from cloudbot.util import http
from BeautifulSoup import BeautifulSoup


@hook.command(autohelp=False)
def word(text):
    "<word> - Gets the word of the day."
    page = http.get('http://merriam-webster.com/word-of-the-day')

    soup = BeautifulSoup(page)

    word = soup.find('strong', {'class': 'main_entry_word'}).renderContents()
    function = soup.find('p', {'class': 'word_function'}).renderContents()

    return "The word of the day is: \x02{}\x02 ({})".format(word, function)
