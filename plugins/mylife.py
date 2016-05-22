import asyncio
import random
import re
import functools

from bs4 import BeautifulSoup
import requests

from cloudbot import hook

fml_cache = []
mlia_cache = []


@asyncio.coroutine
def refresh_fml_cache(loop):
    """ gets a page of random FMLs and puts them into a dictionary """
    url = 'http://www.fmylife.com/random/'
    try:
        _func = functools.partial(requests.get, url, timeout=6)
        request = yield from loop.run_in_executor(None, _func)
        soup = BeautifulSoup(request.text)

        for e in soup.find_all('div', {'class': re.compile('article')}):
            fml_id = int(e['id'])
            text = ''.join(e.find('p').find_all(text=True))
            fml_cache.append((fml_id, text))
    except:
        pass


@asyncio.coroutine
def refresh_mlia_cache(loop):
    """ gets a page of random MLIAs and puts them into a dictionary """
    url = 'http://mylifeisaverage.com/{}'.format(random.randint(1, 11000))
    try:
        _func = functools.partial(requests.get, url, timeout=6)
        request = yield from loop.run_in_executor(None, _func)
        soup = BeautifulSoup(request.text)

        for story in soup.find_all('div', {'class': 'story '}):
            mlia_id = story.find('span', {'class': 'left'}).a.text
            mlia_text = story.find('div', {'class': 'sc'}).text
            mlia_text = " ".join(mlia_text.split())
            mlia_cache.append((mlia_id, mlia_text))
    except:
        pass


@asyncio.coroutine
@hook.on_start()
def initial_refresh(loop):
    # do an initial refresh of the caches
    yield from refresh_fml_cache(loop)
    yield from refresh_mlia_cache(loop)


@asyncio.coroutine
@hook.command(autohelp=False)
def fml(reply, loop):
    """- gets a random quote from fmylife.com"""

    if fml_cache:
        # grab the last item in the fml cache and remove it
        fml_id, text = fml_cache.pop()
        # reply with the fml we grabbed
        reply('(#{}) {}'.format(fml_id, text))
    else:
        yield from refresh_fml_cache(loop)

    # refresh fml cache if its getting empty
    if len(fml_cache) < 3:
        yield from refresh_fml_cache(loop)


@asyncio.coroutine
@hook.command(autohelp=False)
def mlia(reply, loop):
    """- gets a random quote from MyLifeIsAverage.com"""

    if mlia_cache:
        # grab the last item in the mlia cache and remove it
        mlia_id, text = mlia_cache.pop()
        # reply with the mlia we grabbed
        reply('({}) {}'.format(mlia_id, text))
    else:
        yield from refresh_mlia_cache(loop)

    # refresh mlia cache if its getting empty
    if len(mlia_cache) < 3:
        yield from refresh_mlia_cache(loop)
