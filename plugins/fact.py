import re
from util import hook, http, misc
from BeautifulSoup import BeautifulSoup

@hook.command(autohelp=False)
def fact(inp, say=False, nick=False):
    ".fact -- gets a fact from OMGFACTS"

    fact = None
    while fact is None:
        try:
            fact, link = get_fact()
        except:
             pass

    return "%s [ %s ]" % (fact, link)  

    

def get_fact():
    page = http.get('http://www.omg-facts.com/random')
    soup = BeautifulSoup(page)
    container = soup.find('a', {'class' : 'surprise'})
    link = container['href']

    fact = misc.strip_html(container.renderContents())

    if fact:
        return (fact, link)
    else:
        raise nofact
