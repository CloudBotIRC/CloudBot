import requests

from cloudbot import hook
from cloudbot.util import formatting, web

base_url = 'https://www.googleapis.com/books/v1/'
book_search_api = base_url + 'volumes?'


@hook.on_start()
def load_key(bot):
    global dev_key
    dev_key = bot.config.get("api_keys", {}).get("google_dev_key", None)


@hook.command("books", "gbooks")
def books(text):
    """books <query> -- Searches Google Books for <query>."""
    if not dev_key:
        return "This command requires a Google Developers Console API key."

    json = requests.get(book_search_api, params={"q": text, "key": dev_key, "country": "US"}).json()

    if json.get('error'):
        if json['error']['code'] == 403:
            print(json['error']['message'])
            return "The Books API is off in the Google Developers Console (or check the console)."
        else:
            return 'Error performing search.'

    if json['totalItems'] == 0:
        return 'No results found.'

    book = json['items'][0]['volumeInfo']
    title = book['title']
    try:
        author = book['authors'][0]
    except KeyError:
        try:
            author = book['publisher']
        except KeyError:
            author = "Unknown Author"

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

    link = web.shorten(book['infoLink'], service="goo.gl", key=dev_key)

    return "\x02{}\x02 by \x02{}\x02 ({}){} - {} - {}".format(title, author, year, pages, description, link)
