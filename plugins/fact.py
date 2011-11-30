import re
from util import hook, http, misc
from BeautifulSoup import BeautifulSoup

@hook.command(autohelp=False)
def fact(inp, say=False, nick=False):
    ".fact -- gets a fact from OMGFACTS"
    page = http.get('http://www.omg-facts.com/random')

    soup = BeautifulSoup(page)

    container = soup.find('a', {'class' : 'surprise'})

    link = container['href']

    fact = misc.strip_html(container.renderContents())

    return "%s [%s]" % (fact, link)
