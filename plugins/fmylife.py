# Plugin by Lukeroge

from util import hook, http
from BeautifulSoup import BeautifulSoup
from collections import defaultdict

fml_cache = defaultdict()


def refresh_cache():
    """ gets a page of random FMLs and puts them into a dictionary """
    page = http.get('http://www.fmylife.com/random/')
    soup = BeautifulSoup(page)

    for e in soup.findAll('div', {'class': 'post article'}):
        id = int(e['id'])
        # get the text of the FML
        text = ''.join(e.find('p').findAll(text=True))
        text = http.unescape(text)
        # append to the dictionary
        fml_cache[id] = text

# do an initial refresh of the cache
refresh_cache()


@hook.command(autohelp=False)
def fml(inp, reply=None):
    ".fml -- Gets a random quote from fmyfife.com."

    # grab the last item in the fml cache and remove it
    id, text = fml_cache.popitem()
    # reply with the fml we grabbed
    reply('(#%d) %s' % (id, text))
    # refresh fml cache if its getting empty
    if len(fml_cache) < 3:
        refresh_cache()
