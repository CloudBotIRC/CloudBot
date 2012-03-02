# Plugin by Lukeroge
# <lukeroge@gmail.com> <https://github.com/lukeroge/CloudBot/>

import re

from util import hook, http, misc
from urllib2 import HTTPError
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup

base_url = 'http://www.fmylife.com/'

@hook.command(autohelp=False)
def fml(inp):
    ".fml [id] -- Gets a random quote from fmyfife.com. Optionally gets [id]."

    inp = inp.replace("#", "")

    if inp:
        if not inp.isdigit():
            return "Invalid ID!"
        try:
            page = http.get(urljoin(base_url, inp))
        except (HTTPError, IOError):
            return "Could not fetch #%s. FML" % inp
    else:
        try:
            page = http.get(urljoin(base_url, 'random'))
        except (HTTPError, IOError):
            return "I tried to use .fml, but it was broken. FML"

    soup = BeautifulSoup(page)

    soup.find('div', id='submit').extract()
    post = soup.body.find('div', 'post')
    try:
        id = int(post.find('a', 'fmllink')['href'].split('/')[-1])
    except TypeError:
        return "Could not fetch #%s. FML" % inp
    body = misc.strip_html(' '.join(link.renderContents() for link in post('a', 'fmllink')))
    return '(#%d) %s' % (id, body)
