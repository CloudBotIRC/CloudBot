import requests
import random

from cloudbot import hook

api_url = 'http://api.giphy.com/v1/gifs'

@hook.on_start()
def load_api(bot):
    """Loads the API key. Check here for the public api key: https://github.com/Giphy/GiphyAPI"""
    global api_key
    api_key = bot.config.get("api_keys", {}).get("giphy", None)

@hook.command("gif", "giphy")
def giphy(text, chan):
    """Searches giphy.com for a gif using the provided search term."""
    term = text.strip()
    search_url = api_url + '/search'
    params = {
        'q': term,
        'limit': 10,
        'fmt': "json",
        'api_key':api_key
    }
    results = requests.get(search_url, params=params)
    r = results.json()
    if not r['data']:
        return "no results found."
    gif = random.choice(r['data'])
    if gif['rating']:
        out = "{} content rating: \x02{}\x02. (Powered by GIPHY)".format(gif['embed_url'], gif['rating'].upper())
    else:
        out = "{} - (Powered by GIPHY)".format(gif['embed_url'])
    return out
