import re
from util import hook, http
from bs4 import BeautifulSoup


@hook.command(autohelp=False)
def fact(inp, say=False, nick=False):
    "fact -- Gets a random fact from OMGFACTS."

    fact = None
    while fact is None:
        try:
            fact, link = get_fact()
        except:
            pass

    return u"%s [ %s ]" % (fact, link)


def get_fact():
    page = http.get('http://www.omg-facts.com/random')
    soup = BeautifulSoup(page)
    response = soup.find('a', {'class': 'surprise'})
    link = response['href']

    fact = response.contents[0]

    if fact:
        return (fact, link)
    else:
        raise nofact
