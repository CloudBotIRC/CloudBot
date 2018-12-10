import re
import requests

from cloudbot import hook
import cloudbot

@hook.on_start()
def load_api(bot):
    global isbndb_key
    global cx

    isbndb_key = bot.config.get("api_keys", {}).get("isbndb_dev_key", None)

def getISBN(book):
    try:
        url = "http://isbndb.com/api/v2/json/{}/book/".format(isbndb_key)
        url = url + book
        #print(url)
        resp = requests.get(url=url)
        if resp.status_code == 429:
            return {'error': "Too many requests"}
        data = resp.json()
        return data
    except:
        return {'error': "Nothing found, try a different ISBN"}

@hook.command()
def isbn(reply, text):
    """<isbn> -- gets book information"""
    if not isbndb_key:
        return "This command requires a ISBNdb API key."
    sym = text.strip().lower()

    tmpdata = getISBN(sym)

    if 'error' in tmpdata:
        return("{}".format(tmpdata['error']))
    data = tmpdata['data'][0]

    reply("ISBN Lookup | Title: \x02{title}\x02 | Physical Description: \x02{physical_description_text}\x02 | Edition Info: \x02{edition_info}\x02 | Dewey Decimal: \x02{dewey_decimal}\x02".format(**data))
    reply("Summary: {summary}".format(**data))
    for author in data['author_data']:
        reply("Author: {}".format(author['name']))
    return("Long Title: {title_long}".format(**data))
