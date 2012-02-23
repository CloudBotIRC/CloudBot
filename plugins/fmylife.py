import re

from util import hook, http, misc
from urllib2 import HTTPError
from BeautifulSoup import BeautifulSoup

url = 'http://www.fmylife.com/random'

@hook.command(autohelp=False)
def fml(inp):
    ".fml -- gets a random quote from fmyfife.com"

    try:
        page = http.get(url)
    except (HTTPError, IOError):
        return "I tried to use .fml, but it was broken. FML"

    soup = BeautifulSoup(page)

    soup.find('div', id='submit').extract()
    post = soup.body.find('div', 'post')
    id = int(post.find('a', 'fmllink')['href'].split('/')[-1])
    body = misc.strip_html(' '.join(link.renderContents() for link in post('a', 'fmllink')))
    return '(#%d) %s' % (id, body)
