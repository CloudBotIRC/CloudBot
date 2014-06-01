import json

from bs4 import BeautifulSoup

from cloudbot import hook, http, formatting


@hook.command()
def suggest(text):
    """suggest <phrase> -- Gets suggested phrases for a google search"""

    page = http.get('http://google.com/complete/search',
                    output='json', client='hp', q=text)
    page_json = page.split('(', 1)[1][:-1]

    suggestions = json.loads(page_json)[1]
    suggestions = [suggestion[0] for suggestion in suggestions]

    if not suggestions:
        return 'no suggestions found'

    out = ", ".join(suggestions)

    # defuckify text (might not be needed now, but I'll keep it)
    soup = BeautifulSoup(out)
    out = soup.get_text()

    return formatting.truncate_str(out, 200)
