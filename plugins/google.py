# RoboCop 2's gsearch.py - A replacement for google.py after Google's deprecation of Google Web Search API
# Module requires a Google Custom Search API key and a Custom Search Engine ID in order to function.

import random

import urllib.request, urllib.parse

from cloudbot import hook
from cloudbot.util import http, formatting

API_CS = 'https://www.googleapis.com/customsearch/v1?cx={}&q={}&key={}'

@hook.on_start()
def load_api(bot):
    global dev_key
    global cx

    dev_key = bot.config.get("api_keys", {}).get("google_dev_key", None)
    cx = bot.config.get("api_keys", {}).get("google_cse_id", None)

def api_get(query, bot):
    """Use the RESTful Google Search API"""
    # YOU NEED A KEY TO USE THIS MODULE!!!
    # [key] is your Google Developers Project API Key, and [cx] is the custom search engine ID to use for requests.

    url = API_CS.format(urllib.parse.quote(cx), query, urllib.parse.quote(dev_key))
    return http.get_json(url)

@hook.command('g','gse')
def gse(text, bot):
    """google <query> -- Returns first google search result for <query>."""
    if not dev_key:
        return "This command requires a Google Developers Console API key."

    eval = urllib.parse.quote(text)
    parsed = api_get(eval, bot)

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
