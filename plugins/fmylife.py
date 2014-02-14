from util import hook, http

fml_cache = []


def refresh_cache():
    """ gets a page of random FMLs and puts them into a dictionary """
    soup = http.get_soup('http://www.fmylife.com/random/')

    for e in soup.find_all('div', {'class': 'post article'}):
        fml_id = int(e['id'])
        text = ''.join(e.find('p').find_all(text=True))
        fml_cache.append((fml_id, text))

# do an initial refresh of the cache
refresh_cache()


@hook.command(autohelp=False)
def fml(inp, reply=None):
    """fml -- Gets a random quote from fmyfife.com."""

    # grab the last item in the fml cache and remove it
    fml_id, text = fml_cache.pop()
    # reply with the fml we grabbed
    reply('(#{}) {}'.format(fml_id, text))
    # refresh fml cache if its getting empty
    if len(fml_cache) < 3:
        refresh_cache()
