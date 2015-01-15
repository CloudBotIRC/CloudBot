import requests
import json

from cloudbot import hook
from cloudbot.util import formatting

base_url = 'https://www.googleapis.com/books/v1/'
book_search_api = base_url + 'volumes?'


# shrt by petermanser - https://github.com/petermanser/shrt/blob/master/shrt.py
def shrt(url):
    r = requests.post('https://www.googleapis.com/urlshortener/v1/url',
                      data=json.dumps({"longUrl": url}),
                      headers={'content-type': 'application/json'})

    content = json.loads(r.content.decode("UTF-8"))
    if r.status_code == 200:
        return content['id']
    else:
        return "%s: %s" % (content['code'], content['message'])


@hook.on_start()
def load_key(bot):
    global dev_key
    dev_key = bot.config.get("api_keys", {}).get("google_dev_key")


@hook.command("books", "gbooks")
def books(text):
    """books <query> -- Searches Google Books for <query>."""
    json = requests.get(book_search_api, params={"q": text, "key": dev_key}).json()

    if 'error' in json:
        return 'Error performing search.'

    if json['totalItems'] == 0:
        return 'No results found.'

    book = json['items'][0]['volumeInfo']
    title = book['title']
    author = book['authors'][0]

    try:
        description = formatting.truncate_str(book['description'], 130)
    except KeyError:
        description = "No description available."

    try:
        year = book['publishedDate'][:4]
    except KeyError:
        year = "No Year"

    try:
        page_count = book['pageCount']
        pages = ' - \x02{:,}\x02 page{}'.format(page_count, "s"[page_count == 1:])
    except KeyError:
        pages = ''

    link = shrt(book['infoLink'])

    return "\x02{}\x02 by \x02{}\x02 ({}){} - {} - {}".format(title, author, year, pages, description, link)
