import json

from util import hook, http, text
from bs4 import BeautifulSoup


@hook.command
def suggest(inp):
    """suggest <phrase> -- Gets suggested phrases for a google search"""

    page = http.get('http://google.com/complete/search',
                    output='json', client='hp', q=inp)
    page_json = page.split('(', 1)[1][:-1]

    suggestions = json.loads(page_json)[1]
    suggestions = [suggestion[0] for suggestion in suggestions]

    if not suggestions:
        return 'no suggestions found'

    out = u", ".join(suggestions)

    # defuckify text
    soup = BeautifulSoup(out)
    out = soup.get_text()

    return text.truncate_str(out, 200)
