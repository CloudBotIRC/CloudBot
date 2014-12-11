import asyncio
import random

from bs4 import BeautifulSoup
import requests

from cloudbot import hook

mlia_cache = []


@asyncio.coroutine
def refresh_cache(loop):
    """ gets a page of random MLIAs and puts them into a dictionary """
    url = 'http://mylifeisaverage.com/{}'.format(random.randint(1, 11000))
    request = yield from loop.run_in_executor(None, requests.get, url)
    soup = BeautifulSoup(request.text)

    for story in soup.find_all('div', {'class': 'story '}):
        mlia_id = story.find('span', {'class': 'left'}).a.text
        mlia_text = story.find('div', {'class': 'sc'}).text
        mlia_text = " ".join(mlia_text.split())
        mlia_cache.append((mlia_id, mlia_text))


@asyncio.coroutine
@hook.onload()
def initial_refresh(loop):
    # do an initial refresh of the cache
    yield from refresh_cache(loop)


@asyncio.coroutine
@hook.command(autohelp=False)
def mlia(reply, loop):
    """- gets a random quote from MyLifeIsAverage.com"""

    # grab the last item in the mlia cache and remove it
    mlia_id, text = mlia_cache.pop()
    # reply with the mlia we grabbed
    reply('({}) {}'.format(mlia_id, text))
    # refresh mlia cache if its getting empty
    if len(mlia_cache) < 3:
        yield from refresh_cache(loop)
