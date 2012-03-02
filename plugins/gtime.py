import re

from util import hook, http
from BeautifulSoup import BeautifulSoup


@hook.command("time")
def clock(inp, say=None):
    ".time <area> -- Gets the time in <area>"

    white_re = re.compile(r'\s+')
    tags_re = re.compile(r'<[^<]*?>')

    page = http.get('http://www.google.com/search', q="time in " + inp)

    soup = BeautifulSoup(page)

    response = soup.find('td', {'style' : 'font-size:medium'})

    if response is None:
        return "Could not get the time for " + inp + "!"

    output = response.renderContents()

    output = ' '.join(output.splitlines())
    output = output.replace("\xa0", ",")

    output = white_re.sub(' ', output.strip())
    output = tags_re.sub('\x02', output.strip())

    output = output.decode('utf-8', 'ignore')

    return output
