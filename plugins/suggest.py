import json
import requests

from cloudbot import hook
from cloudbot.util import formatting


@hook.command()
def suggest(text):
    """suggest <phrase> -- Gets suggested phrases for a google search"""
    params = {'output': 'json', 'client': 'hp', 'q': text}

    try:
            request = requests.get('http://google.com/complete/search',
                                   params=params)
            request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get suggestions: {}".format(e)

    page = request.text

    page_json = page.split('(', 1)[1][:-1]

    suggestions = json.loads(page_json)[1]
    suggestions = [suggestion[0] for suggestion in suggestions]

    if not suggestions:
        return 'No suggestions found.'

    out = formatting.strip_html(", ".join(suggestions))

    return formatting.truncate(out, 200)
