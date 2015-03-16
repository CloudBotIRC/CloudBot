# RoboCop 2's gsearch.py - A replacement for google.py after Google's deprecation of Google Web Search API
# Module requires a Google Custom Search API key and a Custom Search Engine ID in order to function.

import requests

from cloudbot import hook
from cloudbot.util import http, formatting

API_CS = 'https://www.googleapis.com/customsearch/v1'


@hook.on_start()
def load_api(bot):
    global dev_key
    global cx

    dev_key = bot.config.get("api_keys", {}).get("google_dev_key", None)
    cx = bot.config.get("api_keys", {}).get("google_cse_id", None)


@hook.command('g', 'google', 'gse')
def gse(text):
    """<query> -- Returns first Google search result for <query>."""
    if not dev_key:
        return "This command requires a Google Developers Console API key."
    if not cx:
        return "This command requires a custom Google Search Engine ID."

    parsed = requests.get(API_CS, params={"cx": cx, "q": text, "key": dev_key}).json()

    try:
        result = parsed['items'][0]
    except KeyError:
        return "No results found."

    title = http.unescape(result['title'])
    title = formatting.truncate_str(title, 60)
    content = http.unescape(result['snippet'])

    if not content:
        content = "No description available."
    else:
        content = http.html.fromstring(content).text_content()
        content = formatting.truncate_str(content, 150)

    return u'{} -- \x02{}\x02: "{}"'.format(result['link'], title, content)

@hook.command('gis','image', 'googleimage')
def gse_gis(text):
    """<query> -- Returns first Google Images result for <query>."""
    if not dev_key:
        return "This command requires a Google Developers Console API key."
    if not cx:
        return "This command requires a custom Google Search Engine ID."

    return "Stuff will eventually happen."