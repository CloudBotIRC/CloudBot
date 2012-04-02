import re
from util import hook, http, misc
from BeautifulSoup import BeautifulSoup


@hook.command(autohelp=False)
def word(inp, say=False, nick=False):
    ".word -- Gets the word of the day."
    page = http.get('http://merriam-webster.com/word-of-the-day')

    soup = BeautifulSoup(page)

    word = soup.find('strong', {'class': 'main_entry_word'}).renderContents()
    function = soup.find('p', {'class': 'word_function'}).renderContents()

    #definitions = re.findall(r'<span class="ssens"><strong>:</strong>'
    #                        r' *([^<]+)</span>', content)

    say("(%s) The word of the day is:"\
        " \x02%s\x02 (%s)" % (nick, word, function))
