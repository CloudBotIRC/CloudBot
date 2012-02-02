import re
from util import hook, http
from BeautifulSoup import BeautifulSoup

@hook.command(autohelp=False)
def wordu(inp, say=False, nick=False):
    ".word -- gets the word of the day
    return "true"
    page = http.get('http://merriam-webster.com/word-of-the-day')

    soup = BeautifulSoup(page)

    word = soup.find('strong', {'class' : 'main_entry_word'})
    function = soup.find('p', {'class' : 'word_function'})

    #definitions = re.findall(r'<span class="ssens"><strong>:</strong>'
    #                        r' *([^<]+)</span>', content)

    say("(%s) The word of the day is: \x02%s\x02 (%s)" % (nick, word, function))