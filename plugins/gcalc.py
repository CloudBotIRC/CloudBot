import re

from util import hook, http, misc
from BeautifulSoup import BeautifulSoup


@hook.command("math")
@hook.command
def calc(inp):
    ".calc <term> -- Calculate <term> with Google Calc."

    white_re = re.compile(r'\s+')

    page = http.get('http://www.google.com/search', q=inp)

    soup = BeautifulSoup(page)

    response = soup.find('h2', {'class': 'r'})

    if response is None:
        return "Could not calculate " + inp

    output = response.renderContents()

    output = ' '.join(output.splitlines())
    output = output.replace("\xa0", ",")
    output = white_re.sub(' ', output.strip())

    output = output.decode('utf-8', 'ignore')
    output = misc.strip_html(output)

    return output
