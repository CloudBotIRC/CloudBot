import re

from util import hook, http, misc
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup


base_url = 'http://www.fmylife.com/'
rand_url = urljoin(base_url, 'random')
spec_url = urljoin(base_url, '%d')
error = 'Today I couldn\'t seem to access fmylife.com.. FML'

@hook.command(autohelp=False)
@hook.command("fml")
def fmylife(inp):

    page = http.get(rand_url)
    soup = BeautifulSoup(page)

    soup.find('div', id='submit').extract()
    post = soup.body.find('div', 'post')
    id = int(post.find('a', 'fmllink')['href'].split('/')[-1])
    body = strip_html(decode(' '.join(link.renderContents() for link in post('a', 'fmllink')), 'utf-8'))
    return u'%s: (%d) %s' % (nick, id, body)