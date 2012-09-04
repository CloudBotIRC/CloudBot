from util import hook, http
from bs4 import BeautifulSoup


@hook.command("math")
@hook.command
def calc(inp):
    "calc <term> -- Calculate <term> with Google Calc."

    page = http.get('http://www.google.com/search', q=inp)
    soup = BeautifulSoup(page, 'lxml')

    response = soup.find('h2', {'class': 'r'})
    if response is None:
        return "Could not calculate '%s'" % inp

    return http.unescape(response.contents[0])
