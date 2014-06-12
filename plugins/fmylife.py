import asyncio

from bs4 import BeautifulSoup
import requests

from cloudbot import hook

fml_cache = []

@asyncio.coroutine
def refresh_cache(loop):
    """ gets a page of random FMLs and puts them into a dictionary """
    response = yield from loop.run_in_executor(None, requests.get, 'http://www.fmylife.com/random/')
    soup = BeautifulSoup(response.text, "lxml")

    for e in soup.find_all('div', {'class': 'post article'}):
        fml_id = int(e['id'])
        text = ''.join(e.find('p').find_all(text=True))
        fml_cache.append((fml_id, text))


@asyncio.coroutine
@hook.onload()
def initial_refresh(loop):
    # do an initial refresh of the cache
    yield from refresh_cache(loop)


@asyncio.coroutine
@hook.command(autohelp=False)
def fml(reply, loop):
    """- gets a random quote from fmyfife.com"""

    # grab the last item in the fml cache and remove it
    fml_id, text = fml_cache.pop()
    # reply with the fml we grabbed
    reply('(#{}) {}'.format(fml_id, text))
    # refresh fml cache if its getting empty
    if len(fml_cache) < 3:
        yield from refresh_cache(loop)
