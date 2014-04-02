from util import hook, http, text
from bs4 import BeautifulSoup


@hook.command
def suggest(inp):
    """suggest <phrase> -- Gets suggested phrases for a google search"""
    suggestions = http.get_json('http://suggestqueries.google.com/complete/search', client='firefox', q=inp)[1]

    if not suggestions:
        return 'no suggestions found'

    out = u", ".join(suggestions)

    # defuckify text (might not be needed now, but I'll keep it)
    soup = BeautifulSoup(out)
    out = soup.get_text()

    return text.truncate_str(out, 200)
