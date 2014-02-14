# Plugin by Infinity - <https://github.com/infinitylabs/UguuBot>

import random

from util import hook, http


mlia_cache = []


def refresh_cache():
    """gets a page of random MLIAs and puts them into a dictionary """
    url = 'http://mylifeisaverage.com/{}'.format(random.randint(1, 11000))
    soup = http.get_soup(url)

    for story in soup.find_all('div', {'class': 'story '}):
        mlia_id = story.find('span', {'class': 'left'}).a.text
        mlia_text = story.find('div', {'class': 'sc'}).text.strip()
        mlia_cache.append((mlia_id, mlia_text))

# do an initial refresh of the cache
refresh_cache()


@hook.command(autohelp=False)
def mlia(inp, reply=None):
    """mlia -- Gets a random quote from MyLifeIsAverage.com."""
    # grab the last item in the mlia cache and remove it
    mlia_id, text = mlia_cache.pop()
    # reply with the mlia we grabbed
    reply('({}) {}'.format(mlia_id, text))
    # refresh mlia cache if its getting empty
    if len(mlia_cache) < 3:
        refresh_cache()
